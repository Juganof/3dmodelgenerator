import os
import re
from typing import Dict, Optional

import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

from login import perform_login

MARKTPLAATS_SEARCH = "https://www.marktplaats.nl/l/"
MARKTPLAATS_MSG_API = "https://api.marktplaats.nl/messages/{ad_id}"
MARKTPLAATS_INBOX_API = "https://api.marktplaats.nl/messages/inbox"


class MarktplaatsBot:
    """Simple bot that logs in, searches listings and negotiates via messages."""

    def __init__(self) -> None:
        self.session = requests.Session()
        self.email = os.getenv("MARKTPLAATS_EMAIL")
        self.password = os.getenv("MARKTPLAATS_PASSWORD")
        if not self.email or not self.password:
            raise RuntimeError("Missing MARKTPLAATS_EMAIL or MARKTPLAATS_PASSWORD")
        perform_login(self.email, self.password, session=self.session)

        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

        # Store negotiation state {ad_id: {"price": float, "stage": str}}
        self.negotiations: Dict[str, Dict[str, str | float]] = {}

    # ----------------------------------------------------- Search & analyse
    def search_and_analyze(self, keyword: str):
        """Search Marktplaats and analyse listings with Gemini."""
        params = {
            "query": keyword,
            "searchInTitleAndDescription": "true",
            "attributes": "condition:broken|defect|for parts",
        }
        resp = self.session.get(MARKTPLAATS_SEARCH, params=params)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        results = []
        for ad in soup.select("li[data-listing-id]")[:20]:  # limit for demo
            ad_id = ad.get("data-listing-id")
            title_el = ad.select_one("h3")
            price_el = ad.select_one(".listing-price")
            if not ad_id or not title_el or not price_el:
                continue
            title = title_el.get_text(strip=True)
            price = self._extract_price(price_el.get_text(strip=True))

            analysis = self.analyze_listing(title, price)
            if "recommend" in analysis.lower():
                message = (
                    f"Hoi! Is de {title} nog beschikbaar? Ziet hij er verder compleet uit?"
                )
                self.send_message(ad_id, message)
                self.negotiations[ad_id] = {"price": price, "stage": "asked"}
            results.append(
                {"id": ad_id, "title": title, "price": price, "analysis": analysis}
            )
        return results

    def analyze_listing(self, title: str, price: float) -> str:
        prompt = (
            f"Assess the listing:\nTitle: {title}\nPrice: {price}\n"
            "Looking for broken coffee machines to repair and resell. "
            "Is this a good purchase? Reply with 'recommend' or 'skip' and a short reason."
        )
        model = genai.GenerativeModel("gemini-pro")
        resp = model.generate_content(prompt)
        return resp.text.strip()

    # ---------------------------------------------------------- Messaging
    def send_message(self, ad_id: str, text: str) -> None:
        payload = {"body": text}
        self.session.post(MARKTPLAATS_MSG_API.format(ad_id=ad_id), json=payload)

    def check_negotiations(self) -> None:
        resp = self.session.get(MARKTPLAATS_INBOX_API)
        if resp.status_code != 200:
            return
        data = resp.json()
        for message in data.get("messages", []):
            ad_id = message.get("adId")
            if not ad_id or ad_id not in self.negotiations:
                continue
            stage = self.negotiations[ad_id]["stage"]
            body = message.get("body", "")

            if stage == "asked":
                counter_price = self.extract_counter_price(body)
                if counter_price:
                    offer = self.generate_counter_offer(counter_price)
                    self.send_message(ad_id, offer)
                    self.negotiations[ad_id]["stage"] = "counter"

            elif stage == "counter":
                reply = body.lower()
                if "deal" in reply or "akkoord" in reply:
                    print(
                        f"Deal reached for ad {ad_id} at {self.negotiations[ad_id]['price']}!"
                    )
                    self.negotiations[ad_id]["stage"] = "accepted"

    def extract_counter_price(self, text: str) -> Optional[float]:
        match = re.search(r"€\s*([0-9,.]+)", text)
        if not match:
            return None
        return float(match.group(1).replace(",", ".").strip())

    def generate_counter_offer(self, seller_price: float) -> str:
        prompt = (
            f"The seller proposes €{seller_price}. "
            "Suggest a polite counter-offer in Dutch for repairing/reselling."
        )
        model = genai.GenerativeModel("gemini-pro")
        resp = model.generate_content(prompt)
        return resp.text.strip()

    # --------------------------------------------------------------- Utils
    def _extract_price(self, text: str) -> float:
        match = re.search(r"([0-9,.]+)", text)
        return float(match.group(1).replace(",", ".")) if match else 0.0
