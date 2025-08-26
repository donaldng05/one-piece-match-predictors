from abc import ABC, abstractmethod
from typing import Dict
import logging
import os
from dotenv import load_dotenv
import re

load_dotenv()

# ATTRIBUTE_MAP = {
#     "physical_strength": "strength",
#     "strength": "strength",
#     "speed": "travel_speed",
#     "speed/agility": "agility",
#     "agility": "agility",
#     "durability": "durability",
#     "endurance": "endurance",
#     "stamina": "stamina",
#     "intelligence": "intelligence",
#     "battle_iq": "battle_iq",
#     "combat_skills": "combat_skills",
#     "weapon_proficiency": "weapon_proficiency",
#     "armament_haki": "armament_haki",
#     "observation_haki": "observation_haki",
#     "conqueror_haki": "conqueror_haki",
#     "devil_fruit": "devil_fruit",
#     "mentality": "mentality",
#     "experience": "experience",
#     # Add more mappings as needed
# }


class BaseLLMRater(ABC):
    def __init__(self):
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

        self.rating_prompt = """
        As a One Piece expert, rate {character_name} on the following attributes from 1-10.
        Use these exact attribute names:
        strength, travel_speed, agility, reaction_speed, offense, defense, endurance, durability, stamina, intelligence, battle_iq, combat_skills, weapon_proficiency, armament_haki, observation_haki, conqueror_haki, devil_fruit, mentality, experience.
        For each attribute, provide:
        1. Rating (1-10)
        2. Brief justification
        """

    @abstractmethod
    async def rate_character(self, character_data: Dict) -> Dict:
        pass

    def _parse_response(self, response_text: str) -> Dict:
        result = {}
        pattern = re.compile(
            r"(?P<attr>[A-Za-z_ ]+)[\:\-\*]*\s*(Rating:)?\s*(?P<score>\d{1,2})(/10)?",
            re.IGNORECASE,
        )
        for match in pattern.finditer(response_text):
            key = match.group("attr").strip().lower().replace(" ", "_")
            try:
                result[key] = float(match.group("score"))
            except Exception:
                result[key] = None
        return result


def build_power_scaling_dict(ratings_dicts: list) -> dict:
    # ratings_dicts: list of dicts from each model, e.g. [{'strength': 10, ...}, ...]
    attributes = [
        "strength",
        "travel_speed",
        "agility",
        "reaction_speed",
        "offense",
        "defense",
        "endurance",
        "durability",
        "stamina",
        "intelligence",
        "battle_iq",
        "combat_skills",
        "weapon_proficiency",
        "armament_haki",
        "observation_haki",
        "conqueror_haki",
        "devil_fruit",
        "mentality",
        "experience",
    ]
    model_names = ["OpenAIRater", "GeminiRater"]
    output = {}
    for attr in attributes:
        values = [rd.get(attr) for rd in ratings_dicts if rd.get(attr) is not None]
        if values:
            mean = round(sum(values) / len(values), 1)
            individual = {
                model: rd.get(attr) for model, rd in zip(model_names, ratings_dicts)
            }
            output[attr] = {"mean": mean, "individual_ratings": individual}
        else:
            output[attr] = {
                "mean": None,
                "individual_ratings": {model: None for model in model_names},
            }
    return output
