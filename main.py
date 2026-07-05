from agent.agent import ask_llm
from agent.planner import create_plan
from agent.researcher import evaluate_research

from tools.search_tool import search_web
from tools.crawler_tool import get_page_text


def run_agent(question: str):

    plan = create_plan(question)

    searched = set()
    documents = ""

    queries = plan.get("search_queries", [question])

    max_rounds = 3

    for round_num in range(max_rounds):

        print(f"\n========== ROUND {round_num + 1} ==========")

        all_results = []

        for query in queries:

            print(f"Searching: {query}")

            results = search_web(query, max_results=3)

            for r in results:

                url = r.get("href", r.get("url", ""))

                if url and url not in searched:
                    searched.add(url)
                    all_results.append(r)

        if not all_results:
            break

        for i, r in enumerate(all_results, 1):

            url = r.get("href", r.get("url", ""))

            print(f"Reading: {url}")

            page = get_page_text(url)

            documents += f"""

SOURCE

Title:
{r.get("title","")}

URL:
{url}

Content:
{page[:8000]}

"""

        evaluation = evaluate_research(question, documents)

        print(evaluation)

        if evaluation.get("enough_information"):
            break

        queries = evaluation.get("next_search_queries", [])

    final_prompt = f"""
You are an expert research assistant.

Question:
{question}

Research:
{documents}

Produce the best possible answer.
"""

    return ask_llm(final_prompt)