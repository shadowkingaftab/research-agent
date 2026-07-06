from tools.base import Tool
from tools.registry import register

from core.cache import cache
from core.logger import logger

from tools.search import search_web
from tools.ranker import rank


class SearchTool(Tool):

    name = "search"

    def run(self, task, context):

        all_results = []

        for query in task.search_queries:

            # -------------------------
            # Cache
            # -------------------------

            cached = cache.get(query)

            if cached is not None:

                logger.log(f"Cache hit: {query}")
                results = cached

            else:

                logger.log(f"Searching: {query}")

                results = search_web(
                    query,
                    max_results=5,
                )

                cache.set(query, results)

            all_results.extend(results)

        # -------------------------
        # Rank search results
        # -------------------------

        ranked_results = rank(all_results)

        task.search_results = ranked_results

        logger.log(
            f"Collected {len(ranked_results)} ranked search results."
        )

        return task


register(SearchTool())