from core.cache import cache
from core.logger import logger
from tools.search import search_web
from tools.ranker import rank


class SearchTool(Tool):

    name = "search"

    def run(self, task):

        all_results = []

        for query in task.search_queries:

            cached = cache.get(query)

            if cached:

                logger.log(f"Cache hit: {query}")

                results = cached

            else:

                logger.log(f"Searching: {query}")

                results = search_web(query, max_results=5)

                cache.set(query, results)

            all_results.extend(results)

        task.search_results = rank(all_results)[:15]

        return task