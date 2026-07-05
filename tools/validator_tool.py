from tools.base import Tool
from tools.registry import register

from core.llm import llm
from core.logger import logger


class ValidatorTool(Tool):

    name = "validate"

    def run(self, task):

        prompt = f"""
You are evaluating research quality.

Original Request:
{task.user_request}

Extracted Information:
{task.extracted_data}

Return ONLY valid JSON.

{{
    "enough_information": true,
    "missing_information": [],
    "next_search_queries": []
}}
"""

        evaluation = llm.generate_json(prompt)

        task.data["evaluation"] = evaluation

        if not evaluation.get("enough_information", False):
            task.search_queries = evaluation.get("next_search_queries", [])

        return task


register(ValidatorTool())