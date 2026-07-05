from agent.agent import ask_llm
import json


def evaluate_research(question: str, documents: str):
    prompt = f"""
You are a research evaluator.

Question:
{question}

Collected Research:
{documents[:30000]}

Return ONLY valid JSON.

{{
    "enough_information": true,
    "reason": "",
    "next_search_queries": []
}}

Rules:
- If enough information exists, set enough_information=true.
- If not, generate better search queries.
- Do not answer the user's question.
"""

    response = ask_llm(prompt)

    try:
        return json.loads(response)
    except Exception:
        return {
            "enough_information": True,
            "reason": "Could not evaluate.",
            "next_search_queries": []
        }