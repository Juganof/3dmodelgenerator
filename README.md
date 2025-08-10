# Marktplaats Login App

This repository provides a simple Python script that logs in to [Marktplaats](https://www.marktplaats.nl/) using credentials stored in a `.env` file.

## Setup

1. Copy `.env.example` to `.env` and fill in your email and password.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the script:
   ```bash
   python login.py
   ```

The script will attempt to authenticate and print the response status code and body.
