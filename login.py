import os
import json
import re
import base64
import io

import requests
from dotenv import load_dotenv
from PIL import Image, ImageDraw

load_dotenv()

LOGIN_PAGE = "https://www.marktplaats.nl/identity/v2/login"
LOGIN_API = "https://www.marktplaats.nl/identity/v2/api/login"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)


def perform_login(email: str, password: str) -> dict:
    """Attempt to log in to Marktplaats with provided credentials.

    During the login flow we generate simple screenshot images that describe
    what the function is doing.  The images are returned as base64 strings so
    the frontend can display them to the user as progress screenshots.
    """
    if not email or not password:
        raise ValueError("Email and password are required")

    screenshots = []

    def _snapshot(text: str) -> None:
        """Create a small image containing the given text and store it."""
        img = Image.new("RGB", (400, 120), color="white")
        draw = ImageDraw.Draw(img)
        draw.text((10, 50), text, fill="black")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        screenshots.append(base64.b64encode(buf.getvalue()).decode("utf-8"))

    session = requests.Session()
    # Pretend to be a regular browser.  Some endpoints respond with 403 when
    # the default ``python-requests`` user agent is used.
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": "application/json, text/plain, */*",
    })

    _snapshot("Fetching login page")
    # Fetch login page to obtain xsrf token and threatMetrix information
    resp = session.get(LOGIN_PAGE)
    resp.raise_for_status()

    # Extract xsrf token
    xsrf_match = re.search(r'"xsrfToken":"([^"]+)"', resp.text)
    if not xsrf_match:
        raise RuntimeError("Unable to find xsrf token on login page")
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
        "email": email,
        "password": password,
        "rememberMe": True,
        "threatMetrix": threat_data,
    }

    headers = {
        "Content-Type": "application/json",
        "X-XSRF-TOKEN": xsrf_token,
        "Referer": LOGIN_PAGE,
        "Origin": "https://www.marktplaats.nl",
    }

    _snapshot("Submitting credentials")
    resp = session.post(LOGIN_API, json=payload, headers=headers)

    _snapshot(f"Received {resp.status_code}")
    return {"status_code": resp.status_code, "text": resp.text, "screenshots": screenshots}


if __name__ == "__main__":
    EMAIL = os.getenv("MARKTPLAATS_EMAIL")
    PASSWORD = os.getenv("MARKTPLAATS_PASSWORD")

    if not EMAIL or not PASSWORD:
        raise SystemExit(
            "Please set MARKTPLAATS_EMAIL and MARKTPLAATS_PASSWORD in the .env file"
        )

    result = perform_login(EMAIL, PASSWORD)
    print(f"Status code: {result['status_code']}")
    print(result["text"])
