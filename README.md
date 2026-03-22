# Books AI Classifier
Automated pipeline that scrapes book data, classifies each title by genre
using OpenAI, and writes the enriched results directly to Google Sheets.

## Features
- Scrapes titles, prices and ratings from books.toscrape.com
- Classifies each book by genre using OpenAI gpt-4o-mini
- Writes enriched data to Google Sheets automatically
- Detects existing records to avoid duplicates on subsequent runs
- Credentials managed securely via .env and credentials.json

## How to use
1. Clone this repository
2. Install dependencies:
```
pip3 install requests beautifulsoup4 gspread google-auth openai python-dotenv
```
3. Set up a Google Cloud project, enable Google Sheets API and Google Drive API
4. Create a Service Account and save the JSON credentias as `credentials.json`
5. Create a Google Sheet named `books-ai-classifier` and share it with your service account email
6. Create a `.env` file with your OpenAI key:
```
OPENAI_API_KEY=your_openai_api_key
```
7. Run:
```
python3 main.py
```

## Tech stack
- Python 3
- requests
- BeautifulSoup4
- OpenAI API (gpt-4o-mini)
- Google Sheets API
- gspread
- python-dotenv