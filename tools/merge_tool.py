from tools.base import Tool
from tools.registry import register

from core.llm import llm
from core.logger import logger


class MergeTool(Tool):

    name = "merge"

    def run(self, task):

        print("\nMerging extracted information...")

        prompt = f"""
You are an expert research analyst.

The following JSON objects were extracted from different parts of a large research corpus.

Merge them into ONE complete JSON object.

Requirements:
- Remove duplicate facts.
- Merge duplicate companies.
- Merge duplicate people.
- Keep the most detailed summary.
- Do not invent information.

Data:

{task.extracted_data}

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

        task.extracted_data = llm.generate_json(prompt)

        logger.log("Merge complete.")

        return task


register(MergeTool())