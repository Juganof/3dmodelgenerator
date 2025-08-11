# Marktplaats Bot

Automates searching for listings (e.g., broken coffee machines), evaluates them with
Gemini, messages the seller, negotiates, and notifies when a deal is reached.

> ⚠️ Use responsibly and check that automation is allowed by Marktplaats’s terms of service.

## Setup

```bash
git clone <your_repo_url>
cd <repo>
cp .env.example .env   # fill in credentials and Gemini key
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
5. Add environment variables in Render dashboard (email, password, gemini key).
6. After deploy, open the service URL.

## Usage

- Visit `/` and enter a keyword (e.g., “koffiemachine”).
- The bot logs in, searches listings, uses Gemini to assess quality, and messages sellers.
- Call `/check` periodically (or set a cron job) to poll for replies and continue
  negotiation.
- When a deal is reached, it prints a message (extend with email, Slack, etc.).

## Notes

This is a minimal demonstration. You may need to adapt selectors, endpoints, or handling
logic if Marktplaats changes its layout or security measures. The negotiation logic is
simple and may require improvement for real-world use.
