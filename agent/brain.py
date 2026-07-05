from core.llm import llm


def decide(task):

    thoughts = "\n".join(task.thoughts[-10:]) if hasattr(task, "thoughts") else "None"

    prompt = f"""
You are the reasoning engine of an autonomous research agent.

Your job is to decide the SINGLE best next action.

GOAL
----------------
{task.goal}

USER REQUEST
----------------
{task.user_request}

CURRENT STATE
----------------
Search Queries:
{task.search_queries}

Documents Collected:
{len(task.documents)}

Research Corpus Length:
{len(task.research_corpus)}

Extracted Data:
{task.extracted_data}

Previous Thoughts:
{thoughts}

AVAILABLE TOOLS
----------------

search
- Search the web using the current search queries.

crawl
- Download webpages from search results.

extract
- Extract structured information from the research corpus.

merge
- Merge extracted information from multiple chunks.

validate
- Decide whether enough information has been collected.
- Suggest additional search queries if necessary.

write
- Produce the final report.

finish
- End the research session.

RULES
----------------
1. Search before crawling.
2. Crawl before extracting.
3. Extract before merging.
4. Merge before writing.
5. Only finish after writing.
6. Never repeat unnecessary actions.
7. If more research is needed, search again.

Return ONLY valid JSON.

{
    "thought": "...",
    "tool": "search"
}
"""

    return llm.generate_json(prompt)