from datetime import datetime
import json
from pathlib import Path

from tools.base import Tool
from tools.registry import register

from core.llm import llm
from core.logger import logger

from exporters.markdown_exporter import MarkdownExporter


class WriterTool(Tool):

    name = "write"

    def __init__(self):

        self.exporter = MarkdownExporter()

    def run(self, task):

        logger.log("Generating final report...")

        prompt = f"""
You are an expert research assistant.

Original User Request:
{task.user_request}

Research Goal:
{task.goal}

Expected Output:
{task.expected_output}

Extracted Information:
{task.extracted_data}

Write a professional research report.

Requirements:

- Answer the user's request completely.
- Use Markdown.
- Use clear headings.
- Use bullet points where appropriate.
- Merge duplicate information.
- Every factual statement should reference its source when available.
- Ignore facts with confidence lower than 0.75.
- Do NOT invent facts.
- Base everything ONLY on the extracted information.
- If information is missing, explicitly state that.
- End with a short conclusion.
"""

        report = llm.generate(prompt)

        header = f"""# {task.goal}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

**User Request:** {task.user_request}

**Documents Crawled:** {len(task.documents)}

**Extracted Chunks:** {len(task.extracted_data) if isinstance(task.extracted_data, list) else 1}

---

"""

        report = header + report

        task.final_answer = report

        logger.log("Final report generated.")

        # -------------------------
        # Export Markdown
        # -------------------------

        try:

            md_path = self.exporter.export(
                task.goal,
                report,
            )

            logger.log(f"Markdown saved: {md_path}")

            task.data["report_path"] = str(md_path)

        except Exception as e:

            logger.log(f"Markdown Export Error: {e}")

        # -------------------------
        # Export JSON
        # -------------------------

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

            with open(json_path, "w", encoding="utf-8") as f:

                json.dump(
                    task.extracted_data,
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