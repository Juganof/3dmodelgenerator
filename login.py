import os
import json
import re
import requests
from dotenv import load_dotenv

load_dotenv()

LOGIN_PAGE = "https://www.marktplaats.nl/identity/v2/login"
LOGIN_API = "https://www.marktplaats.nl/identity/v2/api/login"


def perform_login(
    email: str,
    password: str,
    session: requests.Session | None = None,
) -> dict:
    """Attempt to log in to Marktplaats with provided credentials.

    Parameters
    ----------
    email, password:
        Credentials for the Marktplaats account.
    session:
        Optional requests session to use.  If ``None`` a new session is created
        and returned with the login cookies set.
    """

    if not email or not password:
        raise ValueError("Email and password are required")

    if session is None:
        session = requests.Session()

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
    }

    resp = session.post(LOGIN_API, json=payload, headers=headers)
    resp.raise_for_status()
    return {"status_code": resp.status_code, "text": resp.text}


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
