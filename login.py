import os
import json
import re
import requests
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("MARKTPLAATS_EMAIL")
PASSWORD = os.getenv("MARKTPLAATS_PASSWORD")

if not EMAIL or not PASSWORD:
    raise SystemExit("Please set MARKTPLAATS_EMAIL and MARKTPLAATS_PASSWORD in the .env file")

SESSION = requests.Session()
LOGIN_PAGE = "https://www.marktplaats.nl/identity/v2/login"
LOGIN_API = "https://www.marktplaats.nl/identity/v2/api/login"

# Fetch login page to obtain xsrf token and threatMetrix information
resp = SESSION.get(LOGIN_PAGE)
resp.raise_for_status()

# Extract xsrf token
xsrf_match = re.search(r'"xsrfToken":"([^"]+)"', resp.text)
if not xsrf_match:
    raise SystemExit("Unable to find xsrf token on login page")
xsrf_token = xsrf_match.group(1)

# Extract threatMetrix object
threat_match = re.search(r'"threatMetrix":\{([^}]+)\}', resp.text)
if threat_match:
    threat_json = '{' + threat_match.group(1) + '}'
    try:
        threat_data = json.loads(threat_json)
    except json.JSONDecodeError:
        threat_data = {}
else:
    threat_data = {}

payload = {
    "email": EMAIL,
    "password": PASSWORD,
    "rememberMe": True,
    "threatMetrix": threat_data
}

headers = {
    "Content-Type": "application/json",
    "X-XSRF-TOKEN": xsrf_token
}

resp = SESSION.post(LOGIN_API, json=payload, headers=headers)
print(f"Status code: {resp.status_code}")
print(resp.text)
