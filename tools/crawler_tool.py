from concurrent.futures import as_completed

from tools.base import Tool
from tools.registry import register

from core.thread_pool import executor
from core.cache import cache

from tools.crawler import get_page_text
from core.logger import logger


class CrawlerTool(Tool):

    name = "crawl"

    def run(self, task):

        futures = {}

        # -------------------------
        # Crawl every search result
        # -------------------------

        for result in task.search_results:

            url = result.get("href", result.get("url", ""))

            if not url:
                continue

            if url in task.visited_urls:
                continue

            task.visited_urls.add(url)

            # -------------------------
            # Check page cache
            # -------------------------

            cached = cache.load("pages", url)

            if cached is not None:

                print(f"Using cached page: {url}")

                task.documents.append(
                    {
                        "title": result.get("title", ""),
                        "url": url,
                        "content": cached["content"],
                    }
                )

                continue

            # Download in parallel
            futures[
                executor.submit(get_page_text, url)
            ] = (url, result)

        # -------------------------
        # Wait for downloads
        # -------------------------

        for future in as_completed(futures):

            url, result = futures[future]

            try:

                page = future.result()

                if not page:
                    continue

                cache.save(
                    "pages",
                    url,
                    {
                        "content": page
                    }
                )

                task.documents.append(
                    {
                        "title": result.get("title", ""),
                        "url": url,
                        "content": page,
                    }
                )

                logger.log(f"Crawled: {url}")

            except Exception as e:

                logger.log(f"Crawler Error ({url}): {e}")

        # -------------------------
        # Build research corpus
        # -------------------------

        corpus_parts = []

        for doc in task.documents:

            corpus_parts.append(
                f"""
TITLE:
{doc["title"]}

URL:
{doc["url"]}

CONTENT:
{doc["content"][:6000]}
"""
            )

        task.research_corpus = "\n\n".join(corpus_parts)

        print(f"\nDocuments collected: {len(task.documents)}")

        return task


register(CrawlerTool())