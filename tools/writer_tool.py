from datetime import datetime
import json
from pathlib import Path
from dataclasses import asdict

from tools.base import Tool
from tools.registry import register

from core.llm import llm
from core.logger import logger

from pipeline.citation_builder import citation_builder
from pipeline.retriever import retriever

from exporters.markdown_exporter import MarkdownExporter


class WriterTool(Tool):

    name = "write"

    def __init__(self):

        self.exporter = MarkdownExporter()

    def run(self, task, context):
        logger.log("Generating final report...")

        # ---------------------------------
        # Retrieve only the most relevant evidence
        # ---------------------------------

        relevant_evidence = retriever.retrieve(
            query=task.user_request,
            evidence=context.evidence_store.all(),
            limit=50,
        )
        task.retrieved_evidence = relevant_evidence
        contradictions = task.data.get("contradictions", [])

        if contradictions:
            contradiction_summary = "\n".join(
                f"- \"{c['evidence_a'].fact}\" vs \"{c['evidence_b'].fact}\" "
                f"(severity: {c['severity']})"
                for c in contradictions[:10]
            )
        else:
            contradiction_summary = "None detected."
        prompt = f"""
You are an expert research assistant.

Original User Request:
{task.user_request}

Research Goal:
{task.goal}

Expected Output:
{task.expected_output}

Relevant Evidence:
{relevant_evidence}

Known Contradictions (resolve explicitly, do not silently pick one):
{contradiction_summary}

Write a professional research report.

Requirements:

- Answer the user's request completely.
- Use Markdown.
- Use clear headings.
- Use bullet points where appropriate.
- Merge duplicate information.
- Use only evidence with confidence >= 0.80.
- When two facts conflict, prefer the one with the higher confidence.
- Do not report unsupported claims.
- Do NOT invent facts.
- Base everything ONLY on the relevant evidence provided.
- If information is missing, explicitly state that.
- End with a short conclusion.
"""

        report = llm.generate(prompt)

        header = f"""# {task.goal}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

**User Request:** {task.user_request}

**Documents Crawled:** {len(task.documents)}

**Evidence Items:** {len(task.extracted_data)}

**Relevant Evidence Used:** {len(relevant_evidence)}

---

"""

        report = header + report

        # ---------------------------------
        # Knowledge Graph
        # ---------------------------------

        mermaid = task.data.get("knowledge_graph_mermaid", "")

        if mermaid:
            report += "\n\n---\n\n# Knowledge Graph\n\n" + mermaid + "\n"

        # ---------------------------------
        # Citations
        # ---------------------------------

        try:

            citations = citation_builder.build(relevant_evidence)

            if citations:

                report += "\n\n---\n\n# Sources\n"

                for fact, urls in citations.items():

                    report += f"\n## {fact}\n"

                    for url in urls:

                        report += f"- {url}\n"

        except Exception as e:

            logger.log(f"Citation Error: {e}")

        task.final_answer = report

        logger.log("Final report generated.")

        # ---------------------------------
        # Export Markdown
        # ---------------------------------

        try:

            md_path = self.exporter.export(
                task.goal,
                report,
            )

            logger.log(f"Markdown saved: {md_path}")

            task.data["report_path"] = str(md_path)

        except Exception as e:

            logger.log(f"Markdown Export Error: {e}")

        # ---------------------------------
        # Export JSON
        # ---------------------------------

        try:

            export_dir = Path("exports")
            export_dir.mkdir(exist_ok=True)

            filename = (
                task.goal.lower()
                .replace(" ", "_")
                .replace("/", "_")
                .replace("\\", "_")
            )[:60]

            json_path = export_dir / f"{filename}.json"

            serializable = []

            for item in relevant_evidence:

                try:
                    serializable.append(asdict(item))
                except Exception:
                    serializable.append(item)

            with open(json_path, "w", encoding="utf-8") as f:

                json.dump(
                    serializable,
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

            logger.log(f"JSON saved: {json_path}")

            task.data["json_path"] = str(json_path)

        except Exception as e:

            logger.log(f"JSON Export Error: {e}")

        logger.log("Writer finished.")

        return task


register(WriterTool())