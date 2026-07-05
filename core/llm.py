import json
import time

from google import genai

from config import GEMINI_API_KEY
from core.cache import cache


class LLM:

    def __init__(self):

        self.client = genai.Client(api_key=GEMINI_API_KEY)

        self.model = "gemini-2.5-flash"

    def generate(self, prompt: str):

        cached = cache.load("llm", prompt)

        if cached is not None:

            print("Using cached LLM response.")

            return cached

        retries = 5

        for attempt in range(retries):

            try:

                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                )

                text = response.text

                cache.save("llm", prompt, text)

                return text

            except Exception as e:

                print(f"LLM Error ({attempt + 1}/{retries}):", e)

                if attempt == retries - 1:
                    raise

                time.sleep(2 ** attempt)

    def generate_json(self, prompt: str):

        cached = cache.load("llm", prompt + "_json")

        if cached is not None:

            print("Using cached JSON response.")

            return cached

        text = self.generate(prompt)

        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1:
            raise ValueError("Model did not return JSON.")

        obj = json.loads(text[start:end + 1])

        cache.save("llm", prompt + "_json", obj)

        return obj


llm = LLM()