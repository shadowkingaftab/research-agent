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
- Do NOT invent facts.
- Base everything ONLY on the extracted information.
- If information is missing, explicitly state that.
- End with a short conclusion.
"""

        report = llm.generate(prompt)

        task.final_answer = report

        logger.log("Final report generated.")

        try:

            path = self.exporter.export(
                task.goal,
                report,
            )

            logger.log(f"Report saved to: {path}")

            task.data["report_path"] = str(path)

        except Exception as e:

            logger.log(f"Export Error: {e}")

        return task


register(WriterTool())