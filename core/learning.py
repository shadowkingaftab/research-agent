import os
import json
import urllib.parse
from typing import Dict, Any
from core.logger import logger

class LearningEngine:
    def __init__(self, db_path: str = "./workspace/learning_state.json"):
        self.db_path = db_path
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.log(f"Warning: Failed to load learning state: {e}")
        return {
            "source_reliability": {},  # domain -> {"score": 0.5, "trials": 0}
            "query_effectiveness": {}  # query_hash -> {"avg_yield": 0.0, "trials": 0}
        }

    def _get_domain(self, url: str) -> str:
        try:
            return urllib.parse.urlparse(url).netloc
        except Exception:
            return "unknown"

    def _hash_query(self, query: str) -> str:
        # Simple hash for query grouping to avoid massive dictionary keys
        import hashlib
        return hashlib.md5(query.lower().strip().encode()).hexdigest()[:8]

    def record_query_effectiveness(self, query: str, evidence_yield: int):
        q_hash = self._hash_query(query)
        if q_hash not in self.state["query_effectiveness"]:
            self.state["query_effectiveness"][q_hash] = {"avg_yield": 0.0, "trials": 0, "last_query": query}
        
        state = self.state["query_effectiveness"][q_hash]
        # Exponential moving average for yield
        alpha = 0.3
        state["avg_yield"] = (alpha * evidence_yield) + ((1 - alpha) * state["avg_yield"])
        state["trials"] += 1
        state["last_query"] = query

    def record_source_reliability(self, url: str, yielded_evidence: bool, confidence_delta: float = 0.0):
        domain = self._get_domain(url)
        if domain == "unknown":
            return
            
        if domain not in self.state["source_reliability"]:
            self.state["source_reliability"][domain] = {"score": 0.5, "trials": 0}
        
        state = self.state["source_reliability"][domain]
        # Adjust score based on success and confidence delta
        adjustment = 0.1 if yielded_evidence else -0.15
        adjustment += (confidence_delta * 0.5) # Bonus for high confidence
        
        state["score"] = max(0.1, min(1.0, state["score"] + adjustment))
        state["trials"] += 1

    def get_source_prior(self, url: str) -> float:
        domain = self._get_domain(url)
        return self.state["source_reliability"].get(domain, {}).get("score", 0.5)

    def save(self):
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            with open(self.db_path, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.log(f"Failed to save learning state: {e}")

learning_engine = LearningEngine()