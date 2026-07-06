from concurrent.futures import as_completed

from tools.base import Tool
from tools.registry import register

from core.thread_pool import executor
from core.cache import cache
from core.logger import logger

from tools.crawler import get_page_text

from models.source import Source
from models.document import Document


class CrawlerTool(Tool):

    name = "crawl"

    def run(self, task, context):

        futures = {}

        # -------------------------
        # Crawl search results
        # -------------------------

        for result in task.search_results:

            url = result.get("href", result.get("url", ""))

            if not url:
                continue

            if url in task.visited_urls:
                continue

            task.visited_urls.add(url)

            # -------------------------
            # Check cache
            # -------------------------

            cached_page = cache.get(url)

            if cached_page is not None:

                logger.log(f"Cache hit: {url}")

                document = Document(
                    source=Source(
                        title=result.get("title", ""),
                        url=url,
                    ),
                    content=cached_page,
                )

                context.document_store.add(document)

                task.documents.append(
                    {
                        "title": document.source.title,
                        "url": document.source.url,
                        "content": document.content,
                    }
                )

                continue

            # -------------------------
            # Download page
            # -------------------------

            futures[
                executor.submit(get_page_text, url)
            ] = (url, result)

        # -------------------------
        # Collect downloaded pages
        # -------------------------

        for future in as_completed(futures):

            url, result = futures[future]

            try:

                page = future.result()

                if not page:
                    continue

                cache.set(url, page)

                document = Document(
                    source=Source(
                        title=result.get("title", ""),
                        url=url,
                    ),
                    content=page,
                )

                context.document_store.add(document)

                task.documents.append(
                    {
                        "title": document.source.title,
                        "url": document.source.url,
                        "content": document.content,
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

        logger.log(f"Documents collected: {len(task.documents)}")

        return task


register(CrawlerTool())