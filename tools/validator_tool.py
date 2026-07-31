from tools.base import Tool
from tools.registry import register
from core.llm import llm
from core.logger import logger

class ValidatorTool(Tool):
    name = "validate"

    def run(self, task, context):
        logger.log("Starting evidence validation and contradiction detection...")
        evidence_list = context.evidence_store.all()
        if len(evidence_list) < 2:
            logger.log("Insufficient evidence for validation. Skipping.")
            return task

        facts_to_check = [{
            "fact": item.fact, "source": getattr(item, 'source_url', 'unknown'),
            "confidence": getattr(item, 'confidence', 0.5), "category": getattr(item, 'category', 'unknown')
        } for item in evidence_list if hasattr(item, 'fact') and item.fact]

        prompt = f"""You are an expert fact-checker and contradiction detection engine.
Analyze the following extracted facts. Identify direct contradictions, conflicting confidence levels, or unreliable sources.

Facts: {facts_to_check}

Return ONLY valid JSON:
{{
  "contradictions": [{{"fact_a": "...", "fact_b": "...", "severity": "high"|"medium"|"low", "resolution": "..."}}],
  "low_confidence_items": ["fact 1"],
  "validation_summary": "Brief summary of overall evidence quality."
}}"""

        try:
            result = llm.generate_json(prompt)
            task.data["contradictions"] = result.get("contradictions", [])
            task.data["low_confidence_items"] = result.get("low_confidence_items", [])
            task.data["validation_summary"] = result.get("validation_summary", "Validation complete.")

            for c in task.data["contradictions"]:
                if c.get("severity") in ["high", "medium"]:
                    for item in evidence_list:
                        if getattr(item, 'fact', '') == c.get("fact_a") or getattr(item, 'fact', '') == c.get("fact_b"):
                            item.confidence = max(0.1, getattr(item, 'confidence', 0.5) - 0.3)
                            logger.log(f"Downgraded confidence for contradictory fact: {str(item.fact)[:50]}...")
            logger.log(f"Validation complete. Found {len(task.data['contradictions'])} contradictions.")
        except Exception as e:
            logger.log(f"Validation Error: {e}")
            task.data["contradictions"] = []
        return task

register(ValidatorTool())