from agent.agent import ask_llm
from tools.search_tool import search_web
from tools.crawler_tool import get_page_text

while True:

    question = input("\nYou: ")

    if question.lower() in ["exit", "quit"]:
        break

    print("\nSearching...")

    results = search_web(question, max_results=3)

    documents = ""

    for i, r in enumerate(results, 1):

        url = r.get("href", "")

        print(f"Reading page {i}: {url}")

        page = get_page_text(url)

        documents += f"""

SOURCE {i}

URL:
{url}

CONTENT:
{page[:8000]}

"""

    prompt = f"""
You are an expert research assistant.

Answer the user's request using ONLY the information below.

Question:

{question}

Research:

{documents}

If one page is insufficient, combine information from multiple pages.

Do not tell the user to visit the links unless absolutely necessary.
"""

    answer = ask_llm(prompt)

    print("\n====================")
    print(answer)