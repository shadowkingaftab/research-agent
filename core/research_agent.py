from agent.agent import ask_llm
from agent.planner import create_plan
from agent.researcher import evaluate_research

from tools.search import search_web
from tools.crawler import get_page_text

from core.models import Task


class ResearchAgent:

    def run(self, question: str):

        # Create task
        task = Task(user_request=question)

        # Planning
        plan = create_plan(question)

        task.goal = question
        task.task_type = plan.get("task_type", "general")
        task.expected_output = plan.get("expected_output", "answer")
        task.search_queries = plan.get("search_queries", [question])

        max_rounds = 3

        for round_num in range(max_rounds):

            print(f"\n========== ROUND {round_num + 1} ==========")

            all_results = []

            # Search
            for query in task.search_queries:

                print(f"Searching: {query}")

                results = search_web(query, max_results=3)

                for r in results:

                    url = r.get("href", r.get("url", ""))

                    if url and url not in task.visited_urls:
                        task.visited_urls.add(url)
                        all_results.append(r)

            if not all_results:
                print("No new search results.")
                break

            # Crawl
            for r in all_results:

                url = r.get("href", r.get("url", ""))

                print(f"Reading: {url}")

                try:
                    page = get_page_text(url)

                    task.documents.append({
                        "title": r.get("title", ""),
                        "url": url,
                        "content": page
                    })

                except Exception as e:
                    print(f"Failed: {url}")
                    print(e)

            # Build research text for evaluator
            research = ""

            for doc in task.documents:

                research += f"""

TITLE:
{doc['title']}

URL:
{doc['url']}

CONTENT:
{doc['content'][:8000]}

"""

            # Evaluate whether more research is needed
            evaluation = evaluate_research(question, research)

            print(evaluation)

            if evaluation.get("enough_information", True):
                print("Enough information collected.")
                break

            task.search_queries = evaluation.get(
                "next_search_queries",
                task.search_queries
            )

        # Final research text
        research = ""

        for doc in task.documents:

            research += f"""

TITLE:
{doc['title']}

URL:
{doc['url']}

CONTENT:
{doc['content'][:8000]}

"""

        # Final answer
        final_prompt = f"""
You are an expert research assistant.

Answer the user's request using ONLY the research below.

Question:
{question}

Research:
{research}

Instructions:
- Combine information from multiple sources.
- Remove duplicates.
- Be factual.
- If the user requested a list, provide a complete list.
- If the user requested a comparison, format it as a table.
- If the user requested a recipe, provide ingredients and steps.
"""

        return ask_llm(final_prompt)