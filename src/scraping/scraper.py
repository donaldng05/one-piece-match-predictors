from typing import Dict, List
import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
import httpx
import json

from .llm_rater import BaseLLMRater, build_power_scaling_dict
from .llm_implementations import OpenAIRater, GeminiRater

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class OnePieceCharacterScraper:
    def __init__(self):
        self.base_url = "https://onepiece.fandom.com/wiki"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        # Define character attributes
        self.attributes = {
            "basic_stats": [
                "strength",
                "travel_speed",
                "agility",
                "reaction_speed",
                "offense",
                "defense",
                "endurance",
                "durability",
                "stamina",
            ],
            "combat_skills": [
                "intelligence",
                "battle_iq",
                "combat_skills",
                "weapon_proficiency",
            ],
            "haki_abilities": ["armament_haki", "observation_haki", "conqueror_haki"],
            "other_factors": ["devil_fruit", "mentality", "experience"],
        }

        self.raters = [
            OpenAIRater(),
            GeminiRater(),
            # GrokRater(),
            # PerplexityRater(),
        ]

    async def get_page(self, url: str) -> BeautifulSoup:
        """
        Fetch and parse a webpage asynchronously.

        Args:
            url: The URL to fetch

        Returns:
            BeautifulSoup object of the parsed page
        """
        try:
            async with httpx.AsyncClient(
                headers=self.headers, follow_redirects=True
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                return BeautifulSoup(response.text, "html.parser")
        except httpx.RequestError as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    async def process_character(self, character_name: str):
        soup = await self.get_page(f"{self.base_url}/{character_name}")
        wiki_data = self.extract_character_data(soup)
        ratings = []
        for rater in self.raters:
            rating = await rater.rate_character(wiki_data)
            ratings.append(rating)
        power_scaling = build_power_scaling_dict(ratings)
        return {"wiki_data": wiki_data, "power_scaling": power_scaling}

    def extract_character_data(self, soup: BeautifulSoup) -> Dict:
        """
        Extract character information and power scaling data.

        This will require manual data curation and validaftion since
        power scaling is often subjective and not directly stated in wiki.
        """
        character_data = {
            "name": None,
            "title": None,
            "affiliation": None,
            "bounty": None,
        }

        # Add all attributes with None default values
        for category in self.attributes.values():
            for attr in category:
                character_data[attr] = None

        try:
            # Basic character info
            name_element = soup.find("h1", class_="page-header__title")
            if name_element:
                character_data["name"] = name_element.text.strip()

            # Extract from infobox
            infobox = soup.find("table", class_="infobox")
            if infobox:
                rows = infobox.find_all("tr")
                for row in rows:
                    header = row.find("th")
                    value = row.find("td")
                    if header and value:
                        key = header.text.strip().lower()
                        if "bounty" in key:
                            character_data["bounty"] = value.text.strip()
                        elif "affiliation" in key:
                            character_data["affiliation"] = value.text.strip()
                        elif "title" in key:
                            character_data["title"] = value.text.strip()

            return character_data

        except Exception as e:
            logging.error(f"Error extracting character data: {str(e)}")
            return None

    def save_to_csv(self, data: List[Dict], filename: str = "character_data.csv"):
        df = pd.DataFrame(
            [
                {
                    "wiki_data": json.dumps(item["wiki_data"]),
                    "power_scaling": json.dumps(item["power_scaling"]),
                }
                for item in data
            ]
        )
        output_path = f"data/raw/{filename}"
        df.to_csv(output_path, index=False)
        logging.info(f"Data saved to {output_path}")

    def extract_wiki_data(self, raw_data: dict) -> dict:
        return {
            "name": raw_data.get("name"),
            "title": raw_data.get("title"),
            "affiliation": raw_data.get("affiliation"),
            "bounty": raw_data.get("bounty"),
        }
