# Marktplaats Login App

This repository provides a simple Python script that logs in to [Marktplaats](https://www.marktplaats.nl/) using credentials stored in a `.env` file.  A minimal Flask web interface is included so the script can be run as a small website.

## Setup

1. Copy `.env.example` to `.env` and fill in your email and password.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the script directly:
   ```bash
   python login.py
   ```

## Run the web app

Start the Flask web server:

```bash
flask --app app run
```

Visit <http://localhost:5000> to use the login form.  The page posts to `/login` and displays the status code and response body.

## Deploy on Render (free tier)

1. Push this repository to GitHub.
2. Create an account at [Render](https://render.com/) and select **New Web Service**.
3. Connect the GitHub repository.
4. Use the following settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. After deployment, the site will be accessible at the URL provided by Render.
