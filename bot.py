import json
import os
import re
import time
from typing import Dict

import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

MARKTPLAATS_SEARCH = "https://www.marktplaats.nl/l/"


class MarktplaatsBot:
    """Fetches Marktplaats listings and ranks them with Gemini."""

    def __init__(self) -> None:
        self.session = requests.Session()
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel("gemini-pro")

    def search_and_analyze(self, keyword: str) -> list[Dict[str, str | float]]:
        """Search Marktplaats and analyse listings with Gemini."""
        params = {
            "query": keyword,
            "searchInTitleAndDescription": "true",
            "attributes": "condition:broken|defect|for parts",
        }
        resp = self.session.get(MARKTPLAATS_SEARCH, params=params)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        results: list[Dict[str, str | float]] = []
        for ad in soup.select("li[data-listing-id]")[:20]:  # limit for demo
            ad_id = ad.get("data-listing-id")
            title_el = ad.select_one("h3")
            price_el = ad.select_one(".listing-price")
            if not ad_id or not title_el or not price_el:
                continue
            title = title_el.get_text(strip=True)
            price = self._extract_price(price_el.get_text(strip=True))
            link = f"https://link.marktplaats.nl/{ad_id}"

            analysis = self.analyze_listing(title, price)
            results.append({"id": ad_id, "title": title, "price": price, "link": link, **analysis})
            time.sleep(1)  # simple rate limit to be polite
        return results

    def analyze_listing(self, title: str, price: float) -> Dict[str, str | float]:
        prompt = (
            "You evaluate broken coffee machines for repair and resale.\n"
            f"Title: {title}\nPrice: {price}\n"
            "Provide a JSON object with keys rating (1-5, 5=best), reason, and message (Dutch)."
        )
        resp = self.model.generate_content(prompt)
        try:
            data = json.loads(resp.text)
        except Exception:
            rating_match = re.search(r"rating\s*:?\s*(\d)", resp.text, re.I)
            message_match = re.search(r"message\s*:?\s*(.*)", resp.text, re.I | re.S)
            reason_match = re.search(r"reason\s*:?\s*(.*)", resp.text, re.I | re.S)
            data = {
                "rating": int(rating_match.group(1)) if rating_match else 0,
                "message": message_match.group(1).strip() if message_match else resp.text.strip(),
                "reason": reason_match.group(1).strip() if reason_match else "",
            }
        return data

    def _extract_price(self, text: str) -> float:
        match = re.search(r"([0-9,.]+)", text)
        return float(match.group(1).replace(",", ".")) if match else 0.0
