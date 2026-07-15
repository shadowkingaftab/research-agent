from collections import defaultdict

from tools.base import Tool
from tools.registry import register

from core.logger import logger
from models.evidence import Evidence
from pipeline.evidence_graph import contradiction_detector
from pipeline.evidence_graph import contradiction_detector, knowledge_graph

class MergeTool(Tool):

    name = "merge"

    def run(self, task, context):

        logger.log("Merging evidence...")

        merged = defaultdict(list)

        # ----------------------------------
        # Group evidence by normalized fact
        # ----------------------------------

        for evidence in task.extracted_data:

            if not evidence.fact.strip():
                continue

            key = evidence.fact.strip().lower()

            merged[key].append(evidence)

        merged_evidence = []

        # ----------------------------------
        # Merge each group
        # ----------------------------------

        for group in merged.values():

            first = group[0]

            confidence = 0.0

            support_urls = set()
            support_quotes = set()
            entities = set()
            keywords = set()

            metadata = {}

            for item in group:

                confidence += item.confidence

                support_urls.add(item.source_url)

                support_quotes.update(item.supporting_quotes)

                entities.update(item.entities)

                keywords.update(item.keywords)

                metadata.update(item.metadata)

            confidence /= len(group)

            merged_item = Evidence(

                fact=first.fact,

                category=first.category,

                summary=first.summary,

                source_url=first.source_url,

                source_title=first.source_title,

                document_id=first.document_id,

                chunk_id=first.chunk_id,

                confidence=round(confidence, 3),

                entities=sorted(entities),

                keywords=sorted(keywords),

                supporting_quotes=sorted(support_quotes),

                supporting_sources=sorted(support_urls),

                metadata=metadata,

            )

            merged_item.metadata["support_count"] = len(group)

            merged_item.metadata["source_count"] = len(support_urls)

            merged_evidence.append(merged_item)

        merged_evidence.sort(

            key=lambda x: x.confidence,

            reverse=True,

        )

        task.extracted_data = merged_evidence

        logger.log(

            f"Merged into {len(merged_evidence)} unique evidence items."

        )

        # ----------------------------------
        # Contradiction Detection
        # ----------------------------------

        contradictions = contradiction_detector.find(merged_evidence)

        task.data["contradictions"] = contradictions

        if contradictions:

            logger.log(
                f"Detected {len(contradictions)} possible contradiction(s)."
            )

            for c in contradictions[:5]:

                logger.log(
                    f"  [{c['severity']}] "
                    f"\"{c['evidence_a'].fact}\" vs \"{c['evidence_b'].fact}\""
                )

        return task
        # ----------------------------------
        # Knowledge Graph
        # ----------------------------------

        knowledge_graph.build(merged_evidence)

        task.data["knowledge_graph"] = knowledge_graph.to_dict()
        task.data["knowledge_graph_mermaid"] = knowledge_graph.to_mermaid()

        logger.log(
            f"Knowledge graph: {len(knowledge_graph.nodes)} nodes, "
            f"{len(knowledge_graph.edges)} edges."
        )

register(MergeTool())