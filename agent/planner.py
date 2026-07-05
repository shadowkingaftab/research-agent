from agent.agent import ask_llm
import json


def create_plan(user_request: str):
    prompt = f"""
You are an autonomous research planner.

The user request is:

{user_request}

Return ONLY valid JSON.

Format:

{{
    "needs_web_search": true,
    "task_type": "",
    "search_queries": [],
    "expected_output": "",
    "stop_condition": ""
}}

Rules:
- Generate multiple search queries if needed.
- If the request is simple (e.g. math), set needs_web_search to false.
- expected_output examples:
  - answer
  - table
  - comparison
  - list
  - recipe
  - report
"""

    response = ask_llm(prompt)

    try:
        return json.loads(response)
    except:
        return {
            "needs_web_search": True,
            "task_type": "general",
            "search_queries": [user_request],
            "expected_output": "answer",
            "stop_condition": "Collect sufficient information."
        }