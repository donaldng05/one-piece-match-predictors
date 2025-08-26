from openai import OpenAI
import google.generativeai as genai
from .llm_rater import BaseLLMRater
import os
from dotenv import load_dotenv
from typing import Dict

load_dotenv()


class OpenAIRater(BaseLLMRater):
    def __init__(self):
        super().__init__()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def rate_character(self, character_data: Dict) -> Dict:
        prompt = self.rating_prompt.format(character_name=character_data["name"])
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Rate {character_data['name']}"},
            ],
        )
        print("RAW LLM RESPONSE:", response.choices[0].message.content)
        # Use the parser from BaseLLMRater
        return self._parse_response(response.choices[0].message.content)


class GeminiRater(BaseLLMRater):
    def __init__(self):
        super().__init__()
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    async def rate_character(self, character_data: Dict) -> Dict:
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = self.rating_prompt.format(character_name=character_data["name"])
        # Use synchronous method even in async context
        response = model.generate_content(prompt)
        print("RAW LLM RESPONSE:", response.text)
        return self._parse_response(response.text)


# class GrokRater(BaseLLMRater):
#     def __init__(self):
#         super().__init__()
#         self.api_key = os.getenv("GROK_API_KEY")
#         self.api_url = "https://api.grok.x.com/v1/chat/completions"
#         self.client = AsyncClient()

#     async def rate_character(self, character_data: Dict) -> Dict:
#         prompt = self.rating_prompt.format(character_name=character_data["name"])
#         headers = {"Authorization": f"Bearer {self.api_key}"}

#         response = await self.client.post(
#             self.api_url,
#             headers=headers,
#             json={"model": "grok-1", "messages": [{"role": "user", "content": prompt}]},
#         )
#         return self._parse_response(response.json()["choices"][0]["message"]["content"])


# class PerplexityRater(BaseLLMRater):
#     def __init__(self):
#         super().__init__()
#         self.api_key = os.getenv("PERPLEXITY_API_KEY")
#         self.client = AsyncClient()

#     async def rate_character(self, character_data: Dict) -> Dict:
#         prompt = self.rating_prompt.format(character_name=character_data["name"])
#         headers = {
#             "Authorization": f"Bearer {self.api_key}",
#             "Content-Type": "application/json",
#         }

#         response = await self.client.post(
#             "https://api.perplexity.ai/chat/completions",
#             headers=headers,
#             json={
#                 "model": "pplx-7b-chat",
#                 "messages": [{"role": "user", "content": prompt}],
#             },
#         )
#         return self._parse_response(response.json()["choices"][0]["text"])
