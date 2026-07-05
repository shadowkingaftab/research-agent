from tools.base import Tool
from tools.registry import register

from tools.search import search_web
from core.cache import cache
from core.logger import logger

class SearchTool(Tool):

    name = "search"

    def run(self, task):

        all_results = []

        seen = set()

        for query in task.search_queries:

            logger.log(f"Searching: {query}")

            # -------------------------
            # Check cache
            # -------------------------

            cached = cache.load("search", query)

            if cached is not None:

                logger.log("Using cached search results.")

                results = cached

            else:

                results = search_web(query, max_results=5)

                cache.save("search", query, results)

            # -------------------------
            # Remove duplicate URLs
            # -------------------------

            for result in results:

                url = result.get("href", result.get("url", ""))

                if not url:
                    continue

                if url in seen:
                    continue

                seen.add(url)

                all_results.append(result)

        task.search_results = all_results

        print(f"\nCollected {len(all_results)} unique search results.")

        return task


register(SearchTool())