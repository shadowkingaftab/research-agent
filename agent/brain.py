from core.llm import llm
from core.schemas import CognitiveDecision
from core.context import AgentContext

def decide(task, context: AgentContext = None) -> dict:
    cog_state = context.cognitive_state if context and hasattr(context, 'cognitive_state') else None
            allowed_tools = ["strategize", "crawl", "extract", "validate", "build_kg", "review", "write", "finish"]
    
    if not cog_state:
        # Fallback if context is missing (backward compatibility)
        return {"thought": "No cognitive state available.", "tool": "finish"}

    # Format current epistemic state for the LLM
    knowns_text = "\n".join([f"- {k}" for k in cog_state.knowns[-10:]]) or "None yet."
    unknowns_text = "\n".join([f"- {u}" for u in cog_state.unknowns]) or "None."
    
    # Format recent evidence for context
    recent_evidence = []
    for ev in getattr(task, "extracted_data", [])[-5:]:
        try:
            recent_evidence.append(f"- {ev.fact} (Confidence: {ev.confidence:.2f})")
        except Exception:
            recent_evidence.append(str(ev))
    evidence_text = "\n".join(recent_evidence) or "No new evidence since last step."

        prompt = f"""
You are the core of the Cognitive Search Loop. Your goal is to continuously resolve the user's research objective by identifying knowledge gaps and taking the highest-value next action.

OBJECTIVE: {cog_state.objective}

CURRENT KNOWN FACTS:
{knowns_text}

CURRENT UNKNOWN GAPS:
{unknowns_text}

RECENTLY ACQUIRED EVIDENCE:
{evidence_text}

INSTRUCTIONS:
1. Evaluate the recent evidence. Does it resolve any of the UNKNOWN GAPS?
2. Update the lists of KNOWN FACTS and UNKNOWN GAPS.
3. Determine the highest-value next action. 
   - If you need to search, choose the "strategize" tool. The Strategy Engine will automatically generate multi-hypothesis, multi-modality queries based on the unknowns.
   - If you have enough evidence to write the report, choose "write".
   - If you cannot possibly find the information, set boundary_reached to true.
4. If searching, provide a 'search_focus' that describes the exact concept you want the Strategy Engine to target.

AVAILABLE TOOLS: strategize, crawl, extract, validate, build_kg, review, write, finish

Return ONLY valid JSON:
{{
  "updated_knowns": ["fact 1", "fact 2"],
  "updated_unknowns": ["gap 1"],
  "thought": "Reasoning about the epistemic gap and why this action is best.",
  "tool": "strategize|crawl|extract|validate|build_kg|review|write|finish",
  "search_focus": "Specific concept or question to target",
  "boundary_reached": false,
  "boundary_justification": ""
}}
"""