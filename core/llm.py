import json
import time

from google import genai

from config import GEMINI_API_KEY

from core.cache import cache
from core.logger import logger


class LLM:

    def __init__(self):

        self.client = genai.Client(api_key=GEMINI_API_KEY)

        self.model = "gemini-2.5-flash"

        self.total_requests = 0
        self.total_cache_hits = 0
        self.total_time = 0.0

    # --------------------------------------------------
    # Plain Text Generation
    # --------------------------------------------------

    def generate(self, prompt: str):

        self.total_requests += 1

        cached = cache.get(prompt)

        if cached is not None:

            self.total_cache_hits += 1

            logger.log("LLM Cache Hit")

            return cached

        retries = 5

        last_error = None

        for attempt in range(retries):

            start = time.perf_counter()

            try:

                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                )

                elapsed = time.perf_counter() - start

                self.total_time += elapsed

                logger.log(
                    f"LLM Response ({elapsed:.2f}s)"
                )

                text = response.text

                cache.set(prompt, text)

                return text

            except Exception as e:

                elapsed = time.perf_counter() - start

                last_error = e

                logger.log(
                    f"LLM Error ({attempt + 1}/{retries}) : {e}"
                )

                logger.log(
                    f"Elapsed : {elapsed:.2f}s"
                )

                if attempt < retries - 1:

                    wait = 2 ** attempt

                    logger.log(
                        f"Retrying in {wait} seconds..."
                    )

                    time.sleep(wait)

        raise last_error

    # --------------------------------------------------
    # JSON Generation
    # --------------------------------------------------

    def generate_json(self, prompt: str):

        cache_key = prompt + "_json"

        cached = cache.get(cache_key)

        if cached is not None:

            self.total_cache_hits += 1

            logger.log("LLM JSON Cache Hit")

            return cached

        text = self.generate(prompt)

        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1:

            raise ValueError(
                "Model did not return valid JSON."
            )

        try:

            obj = json.loads(text[start:end + 1])

        except Exception as e:

            logger.log(f"JSON Parse Error: {e}")

            raise

        cache.set(cache_key, obj)

        return obj

    # --------------------------------------------------
    # Statistics
    # --------------------------------------------------

    def stats(self):

        logger.log("")
        logger.log("========== LLM STATS ==========")
        logger.log(f"Requests   : {self.total_requests}")
        logger.log(f"Cache Hits : {self.total_cache_hits}")
        logger.log(f"LLM Time   : {self.total_time:.2f}s")

        if self.total_requests:

            logger.log(
                f"Average    : "
                f"{self.total_time / self.total_requests:.2f}s"
            )

        logger.log("===============================")


llm = LLM()