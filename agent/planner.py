from core.llm import llm
from core.schemas import InitialCognitivePlan
from core.cognitive_state import CognitiveState


def create_plan(question: str, context=None) -> dict:
    prompt = f"""
You are the Intent Resolution and Cognitive Initialization engine.

Your objective is to deeply understand the user's research request, make reasonable assumptions, and establish the initial epistemic state. Do not ask for clarification; infer the intent.

User Request: {question}

Return ONLY valid JSON matching this schema:
{{
  "objective": "The deep, inferred research objective.",
  "initial_knowns": ["Fact 1", "Context 1"],
  "initial_unknowns": ["Specific gap 1", "Specific gap 2"]
}}
"""
    try:
        plan_model = llm.generate_structured(prompt, InitialCognitivePlan)
        plan = plan_model.model_dump()
        
        # Initialize the Cognitive State if context is provided
        if context and hasattr(context, 'cognitive_state'):
            context.cognitive_state.objective = plan.get("objective", question)
            context.cognitive_state.knowns = plan.get("initial_knowns", [])
            context.cognitive_state.unknowns = plan.get("initial_unknowns", [])
            context.cognitive_state.current_focus = plan.get("initial_unknowns", [""])[0]

        # Maintain backward compatibility with the existing engine loop structure
        return {
            "goal": plan.get("objective", question),
            "task_type": "cognitive_research",
            "expected_output": "report",
            "evidence_sufficiency_threshold": 0.85,
            "sub_goals": [{"id": "1", "description": plan.get("objective", question), "search_queries": plan.get("initial_unknowns", [question]), "required_tools": ["search", "crawl", "extract"]}],
            "tools": ["search", "crawl", "extract", "merge", "validate", "build_kg", "review", "write", "finish"]
        }
    except Exception:
        if context and hasattr(context, 'cognitive_state'):
            context.cognitive_state.objective = question
            context.cognitive_state.unknowns = [question]
        return {
            "goal": question, "task_type": "general", "expected_output": "report",
            "evidence_sufficiency_threshold": 0.80,
            "sub_goals": [{"id": "1", "description": question, "search_queries": [question], "required_tools": ["search"]}],
            "tools": ["search", "crawl", "extract", "merge", "validate", "build_kg", "review", "write", "finish"]
        }