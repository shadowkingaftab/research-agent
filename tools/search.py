from ddgs import DDGS


def search_web(query: str, max_results: int = 5):
    try:
        with DDGS() as ddgs:
            return list(ddgs.text(query, max_results=max_results))
    except Exception as e:
        print("Search Error:", e)
        return []