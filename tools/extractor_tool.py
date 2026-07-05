from tools.base import Tool
from tools.registry import register

from core.llm import llm
from core.chunker import chunk_text
from core.logger import logger


class ExtractTool(Tool):

    name = "extract"

    def run(self, task):

        logger.log("Extracting research...")

        chunks = chunk_text(task.research_corpus)

        extracted = []

        total_chunks = len(chunks)

        for i, chunk in enumerate(chunks, start=1):

            logger.log(f"Processing chunk {i}/{total_chunks}")

            prompt = f"""
You are an expert research analyst.

User Request:
{task.user_request}

Research:

{chunk}

Extract every important piece of information.

Return ONLY valid JSON.

{{
    "key_points": [],
    "companies": [],
    "people": [],
    "products": [],
    "facts": [],
    "summary": ""
}}
"""

            try:

                result = llm.generate_json(prompt)

                extracted.append(result)

            except Exception as e:

                print(f"Chunk {i} failed:", e)

        task.extracted_data = extracted

        print(f"Finished extracting {len(extracted)} chunks.")

        return task


register(ExtractTool())