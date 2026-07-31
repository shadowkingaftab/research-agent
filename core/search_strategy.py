import re
from typing import List, Dict, Any
from dataclasses import dataclass, field
from core.logger import logger
from core.llm import llm
from core.schemas import StrategyDecision

@dataclass
class SearchHypothesis:
    id: str
    description: str
    target_unknown: str
    status: str = "active"  # active, confirmed, discarded

@dataclass
class SearchStrategyState:
    hypotheses: List[SearchHypothesis] = field(default_factory=list)
    active_modalities: List[str] = field(default_factory=list)
    source_scores: Dict[str, float] = field(default_factory=dict)
    query_history: List[Dict[str, Any]] = field(default_factory=list)
    iterations: int = 0
    pivot_triggered: bool = False

class SearchStrategyEngine:
    def __init__(self):
        self.modality_map = {
            "technical": ["github", "stackoverflow", "official_docs", "arxiv"],
            "market": ["news", "company_websites", "financial_reports", "industry_blogs"],
            "academic": ["scholar", "arxiv", "research_gate", "university_sites"],
            "general": ["web", "news", "wikipedia"],
            "factual": ["web", "wikipedia", "official_gov_sites"]
        }

    def evaluate_and_adapt(self, task, context) -> List[str]:
        """
        Continuously evaluates the search trajectory and generates the next 
        set of highly optimized, modality-specific queries.
        """
        state = getattr(task, "strategy_state", SearchStrategyState())
        task.strategy_state = state
        state.iterations += 1

        # 1. Detect Diminishing Returns & Evaluate Source Quality
        recent_yield = self._calculate_recent_yield(task)
        self._update_source_scores(task, state)
        
        pivot_required = False
        if recent_yield == 0 and state.iterations > 1:
            logger.log("Strategy Engine: Diminishing returns detected. Triggering strategic pivot.")
            pivot_required = True
            state.pivot_triggered = True

        # 2. Identify missing entities/relationships from current unknowns
        unknowns = context.cognitive_state.unknowns if context else []
        knowns = context.cognitive_state.knowns if context else []

        # 3. Formulate Strategy via LLM
        prompt = self._build_strategy_prompt(task, state, unknowns, knowns, recent_yield, pivot_required)
        
        try:
            decision: StrategyDecision = llm.generate_structured(prompt, StrategyDecision)
            
            # 4. Update State
            state.hypotheses = [
                SearchHypothesis(id=h.id, description=h.description, target_unknown=h.target_unknown)
                for h in decision.hypotheses
            ]
            state.active_modalities = decision.selected_modalities
            
            # 5. Deduplicate and Filter Queries
            final_queries = self._deduplicate_queries(decision.queries, state.query_history)
            
            # Record history
            state.query_history.append({
                "iteration": state.iterations,
                "queries": final_queries,
                "modalities": decision.selected_modalities,
                "yield": recent_yield
            })

            logger.log(f"Strategy Engine: Generated {len(final_queries)} queries across {decision.selected_modalities}.")
            return final_queries

        except Exception as e:
            logger.log(f"Strategy Engine Error: {e}. Falling back to basic query.")
            return [context.cognitive_state.unknowns[0]] if unknowns else [task.user_request]

    def _calculate_recent_yield(self, task) -> int:
        """Calculates how many new facts were extracted in the last search cycle."""
        history = getattr(task, "action_history", [])
        if len(history) < 2:
            return 1 # Assume positive yield on first run
        
        # Find the last search/extract action
        for action in reversed(history):
            if action.get("tool") in ["search", "extract", "crawl"]:
                return action.get("evidence_items", 0) - (action.get("evidence_items", 0) - 1) # Simplified delta
        return 0

    def _update_source_scores(self, task, state: SearchStrategyState):
        """Continuously scores domains based on evidence quality and consistency."""
        for evidence in getattr(task, "extracted_data", []):
            url = getattr(evidence, "source_url", "")
            if not url: continue
            
            domain = re.search(r"(?:https?://)?(?:www\.)?([^/]+)", url)
            if not domain: continue
            domain = domain.group(1)
            
            # Base score adjustment based on confidence
            conf = getattr(evidence, "confidence", 0.5)
            current_score = state.source_scores.get(domain, 0.5)
            
            # Exponential moving average
            alpha = 0.2
            state.source_scores[domain] = (alpha * conf) + ((1 - alpha) * current_score)

    def _deduplicate_queries(self, new_queries: List[str], history: List[Dict]) -> List[str]:
        """Prevents the engine from looping over the same semantic search space."""
        past_queries = set()
        for h in history:
            past_queries.update([q.lower().strip() for q in h.get("queries", [])])
            
        unique = []
        for q in new_queries:
            if q.lower().strip() not in past_queries:
                unique.append(q)
        return unique if unique else new_queries # Fallback if all are dupes

    def _build_strategy_prompt(self, task, state, unknowns, knowns, recent_yield, pivot_required) -> str:
        unknowns_text = "\n".join([f"- {u}" for u in unknowns[:5]]) or "None."
        knowns_text = "\n".join([f"- {k}" for k in knowns[:5]]) or "None."
        past_queries_text = "\n".join([f"- {q}" for h in state.query_history[-3:] for q in h.get("queries", [])]) or "None."
        
        top_domains = sorted(state.source_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        domains_text = ", ".join([f"{d} ({s:.2f})" for d, s in top_domains]) or "No domains scored yet."

        return f"""
You are the Adaptive Search Strategy Engine. Your goal is to maximize information gain by generating highly specific, multi-modality search hypotheses.

OBJECTIVE: {task.user_request}

CURRENT UNKNOWN GAPS:
{unknowns_text}

VERIFIED KNOWN FACTS:
{knowns_text}

PREVIOUS QUERIES (DO NOT REPEAT):
{past_queries_text}

TOP SCORING DOMAINS SO FAR:
{domains_text}

RECENT YIELD: {recent_yield} new facts.
PIVOT REQUIRED: {pivot_required}

INSTRUCTIONS:
1. Analyze the UNKNOWN GAPS. Generate 1-3 distinct search hypotheses to resolve them.
2. Select the most appropriate search modalities (e.g., web, github, scholar, news, company_websites, official_docs). If pivot is required, you MUST select different modalities than previously used.
3. Formulate 2-4 highly specific search queries. Use advanced operators if necessary. DO NOT repeat previous queries.
4. If yield is 0 and pivot is required, broaden the scope or target a completely different entity/relationship.

Return ONLY valid JSON matching the StrategyDecision schema.
"""