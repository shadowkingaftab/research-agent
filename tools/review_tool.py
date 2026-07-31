from tools.base import Tool
from tools.registry import register
from core.llm import llm
from core.logger import logger

class ReviewTool(Tool):
    name = "review"

    def run(self, task, context):
        logger.log("Initiating self-review and report refinement...")
        current_report = task.final_answer or "No report generated yet."

        prompt = f"""You are an expert research quality assurance auditor.
Evaluate the following research report against the original user request and goal.

User Request: {task.user_request}
Research Goal: {task.goal}
Current Report: {current_report[:4000]}

Evaluate based on:
1. Completeness: Does it fully answer the user request?
2. Evidence Traceability: Are claims backed by the extracted evidence?
3. Clarity and Structure: Is it well-formatted in Markdown?
4. Contradictions: Are there any unresolved conflicting facts?

Return ONLY valid JSON:
{{
  "score": 0.0 to 1.0,
  "critique": "Detailed critique of the report's weaknesses.",
  "needs_revision": true or false,
  "revision_instructions": "Specific instructions for the writer tool to improve the report. If needs_revision is false, this should be 'None'."
}}"""

        try:
            result = llm.generate_json(prompt)
            score = result.get("score", 0.0)
            needs_revision = result.get("needs_revision", False)
            
            task.data["review_score"] = score
            task.data["review_critique"] = result.get("critique", "")
            
            if needs_revision and score < 0.85:
                logger.log(f"Report requires revision (Score: {score}). Instructions: {result.get('revision_instructions')}")
                task.data["revision_instructions"] = result.get("revision_instructions")
                task.final_answer = ""  # Force re-write
            else:
                logger.log(f"Report passed quality assurance (Score: {score}).")
                task.data["revision_instructions"] = "None"
        except Exception as e:
            logger.log(f"Review Tool Error: {e}")
            task.data["review_score"], task.data["revision_instructions"] = 0.5, "None"

        return task

register(ReviewTool())