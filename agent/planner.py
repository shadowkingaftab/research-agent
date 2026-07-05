from core.llm import llm


def create_plan(question: str):

    prompt = f"""
You are an autonomous research planner.

Return ONLY valid JSON.

Example:

{{
    "goal":"Find the top AI companies",
    "task_type":"research",
    "expected_output":"report",
    "search_queries":[
        "top AI companies",
        "largest AI startups",
        "AI industry leaders"
    ],
    "tools":[
        "search",
        "crawl",
        "extract",
        "merge",
        "validate",
        "write"
    ]
}}

User Request:
{question}
"""

    return llm.generate_json(prompt)