# Marktplaats Bot

Searches Marktplaats listings (e.g., broken coffee machines), ranks them with Google
Gemini for repair & flip potential, and drafts friendly messages for sellers.

> ⚠️ Use responsibly and check that automation is allowed by Marktplaats’s terms of service.

## Setup

```bash
git clone <your_repo_url>
cd <repo>
cp .env.example .env   # fill in Gemini API key
pip install -r requirements.txt
```

Run locally:

```bash
flask --app app run
# browse http://localhost:5000
```

Deploy on Render:

1. Push repository to GitHub.
2. Create a Web Service on Render connected to the repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Add `GEMINI_API_KEY` in Render dashboard.
6. After deploy, open the service URL.

## Usage

- Visit `/` and enter a keyword (e.g., “koffiemachine”).
- The app scrapes public search results, sends each listing to Gemini for an investment
  rating and a suggested message.
- Results show title, price, rating, link, and an AI-generated message to copy & paste
  to the seller.

## Notes

This is a minimal demonstration. You may need to adapt selectors, prompts, or handling
logic if Marktplaats changes its layout or if you target other items.
