import json
import os
import re
import time
from typing import Dict

import google.generativeai as genai
import requests

MARKTPLAATS_API = "https://www.marktplaats.nl/lrp/api/search"


class MarktplaatsBot:
    """Fetches Marktplaats listings and ranks them with Gemini."""

    def __init__(self) -> None:
        self.session = requests.Session()
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel("gemini-pro")

    def search_and_analyze(self, keyword: str) -> list[Dict[str, str | float]]:
        """Search Marktplaats and analyse listings with Gemini."""
        results: list[Dict[str, str | float]] = []
        offset = 0
        while True:
            params = {"query": keyword, "offset": offset, "limit": 30}
            resp = self.session.get(MARKTPLAATS_API, params=params)
            resp.raise_for_status()
            data = resp.json()
            listings = data.get("listings", [])
            if not listings:
                break
            for item in listings:
                ad_id = item.get("itemId")
                title = item.get("title", "")
                price = item.get("priceInfo", {}).get("priceCents", 0) / 100
                link = f"https://www.marktplaats.nl{item.get('vipUrl', '')}"

                analysis = self.analyze_listing(title, price)
                results.append({"id": ad_id, "title": title, "price": price, "link": link, **analysis})
                time.sleep(1)  # simple rate limit to be polite

            offset += len(listings)
            total = data.get("totalResultCount", 0)
            if offset >= total:
                break
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

