from unittest import result

from core import context
from tools.base import Tool
from tools.registry import register

from core.llm import llm
from core.chunker import chunk_text
from core.logger import logger
from core.evidence_ranker import ranker


class ExtractTool(Tool):

    name = "extract"

    def run(self, task, context):

        logger.log("Starting extraction...")

        if not task.research_corpus.strip():

            logger.log("No research corpus available.")

            return task

        documents = context.document_store.all()

        corpus = ""

        for document in documents:

            corpus += f"""

        TITLE:
        {document.source.title}

        URL:
        {document.source.url}

        CONTENT:
        {document.content}

        """

        chunks = chunk_text(corpus)

        extracted = []

        total_chunks = len(chunks)

        logger.log(f"Research split into {total_chunks} chunks.")

        for i, chunk in enumerate(chunks, start=1):

            logger.log(f"Processing chunk {i}/{total_chunks}")

            prompt = f"""
You are an expert research analyst.

User Request:
{task.user_request}

Research Chunk:

{chunk}

Extract every important piece of information.

For every fact, include the source URL if available.

Return ONLY valid JSON.

{{
    "key_points": [],
    "companies": [],
    "people": [],
    "products": [],
    "facts": [
        {{
            "fact": "",
            "source": "",
            "confidence": 0.75
        }}
    ],
    "summary": ""
}}
"""

            try:

                result = llm.generate_json(prompt)

                extracted.append(result)

                source_url = "unknown"

                if i - 1 < len(context.document_store.all()):
                    source_url = context.document_store.all()[i - 1].source.url

# -------------------------
# Companies
# -------------------------

                for company in result.get("companies", []):

                    evidence = {
                        "type": "company",
                        "value": company,
                        "source": source_url,
                    }

                    context.evidence_store.add(
                        ranker.rank(evidence)
                )
# -------------------------
# People
# -------------------------

                for person in result.get("people", []):

                    evidence = {
                        "type": "company",
                        "value": company,
                        "source": source_url,
                    }

                    context.evidence_store.add(
                        ranker.rank(evidence)
                    )

# -------------------------
# Products
# -------------------------

                for product in result.get("products", []):

                    evidence = {
                        "type": "company",
                        "value": company,
                        "source": source_url,
                    }

                    context.evidence_store.add(
                        ranker.rank(evidence)
                    )

# -------------------------
# Facts
# -------------------------

                for fact in result.get("facts", []):

                    evidence = {
                        "type": "company",
                        "value": company,
                        "source": source_url,
                    }

                    context.evidence_store.add(
                        ranker.rank(evidence)
                    )
# -------------------------
# Summary
# -------------------------

                summary = result.get("summary")

                if summary:

                   evidence = {
                        "type": "company",
                        "value": company,
                        "source": source_url,
                }

                   context.evidence_store.add(
                        ranker.rank(evidence)
            )

                logger.log(f"Chunk {i} extracted successfully.")

            except Exception as e:

                logger.log(f"Chunk {i} failed: {e}")

        task.extracted_data = extracted

        total_facts = 0

        for item in extracted:

            facts = item.get("facts", [])

            if isinstance(facts, list):
                total_facts += len(facts)

        logger.log("========================================")
        logger.log("EXTRACTION COMPLETE")
        logger.log("========================================")
        logger.log(f"Chunks Processed : {total_chunks}")
        logger.log(f"Chunks Extracted : {len(extracted)}")
        logger.log(f"Facts Extracted  : {total_facts}")

        return task


register(ExtractTool())