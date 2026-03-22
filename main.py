# Books AI Classifier
# Scrapes books, classifies them by genre using OpenAI and writes results to Google Sheets

import os
import json
import requests
import gspread
from bs4 import BeautifulSoup
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

load_dotenv()

# OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Google Sheets
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
credentials = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
gsheets = gspread.authorize(credentials)
spreadsheet = gsheets.open("books-ai-classifier")
sheet = spreadsheet.sheet1

URL_BASE = "https://books.toscrape.com/catalogue/page-{}.html"


def scrape_page(page_number):
    url = URL_BASE.format(page_number)
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.content, "html.parser")
    books = soup.find_all("article", class_="product_pod")
    results = []
    for book in books:
        title = book.h3.a["title"]
        price = book.find("p", class_="price_color").text.strip().replace("Â", "")
        rating = book.p["class"][1]
        results.append({"title": title, "price": price, "rating": rating})
    return results

def scrape_all(max_pages=2):
    all_books = []
    for page in range(1, max_pages + 1):
        print(f"Scrapping page {page}/{max_pages}...")
        all_books.extend(scrape_page(page))
    return all_books

def clasify_books(books):
    titles = "\n".join([f"- {b['title']}" for b in books])
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a book classifier. Given a list of book titles, return a JSON array where each item has 'title' and 'genre'. Use only these genres: Fiction, Non-Fiction, Mystery, Romance, Science, History, Fantasy, Self-Help. Respond with raw JSON only, no markdown."
            },
            {
                "role": "user",
                "content": f"Classify these books:\n{titles}"
            }
        ]
    )
    return json.loads(response.choices[0].message.content)

def setup_headers():
    headers = sheet.row_values(1)
    if not headers:
        sheet.update(range_name="A1", values=[["Title", "Price", "Rating", "Genre", "Last Updated"]])
        print("Headers created.")

def get_existing_titles():
    data = sheet.get_all_records()
    return {row["Title"] for row in data}

def update_sheet(books, classifications):
    genre_map = {item["title"]: item["genre"] for item in classifications}
    existing_titles = get_existing_titles()
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    new_rows = []

    for book in books:
        if book["title"] not in existing_titles:
            genre = genre_map.get(book["title"], "Unknown")
            new_rows.append([book["title"], book["price"], book["rating"], genre, date])
    if new_rows:
        sheet.append_rows(new_rows, value_input_option="USER_ENTERED")
        print(f"Sheet updated: {len(new_rows)} rows added.")
    else:
        print("No new books found.")


# Run
print ("Starting Books AI Classifier...\n")
setup_headers()
books = scrape_all(max_pages=2)
print(f"\nClassifying {len(books)} books with AI...")
classifications = clasify_books(books)
update_sheet(books, classifications)
print("\nDone! Check your Google Sheet.")
