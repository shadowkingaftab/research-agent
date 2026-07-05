from ddgs import DDGS

def search_web(query, max_results=5):
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))

    print("\nDEBUG RESULTS:")
    print(results)

    return results