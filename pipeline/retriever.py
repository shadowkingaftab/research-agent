from typing import List, Any

class Retriever:
    def retrieve(self, query: str, evidence: List[Any], limit: int = 50, k: int = 60) -> List[Any]:
        if not evidence:
            return []

        semantic_scores, keyword_scores = {}, {}
        query_terms = set(query.lower().split())

        for idx, item in enumerate(evidence):
            text = " ".join([
                str(getattr(item, 'fact', '')), str(getattr(item, 'summary', '')),
                " ".join(getattr(item, 'entities', [])), " ".join(getattr(item, 'keywords', []))
            ]).lower()
            
            term_matches = sum(1 for term in query_terms if term in text)
            keyword_scores[idx] = term_matches / len(query_terms) if query_terms else 0.0

            if hasattr(item, 'embedding') and item.embedding is not None:
                semantic_scores[idx] = 0.5 + (keyword_scores[idx] * 0.5)
            else:
                semantic_scores[idx] = keyword_scores[idx] * 0.8

        rrf_scores = {}
        for idx in range(len(evidence)):
            rank_semantic = sorted(semantic_scores.keys(), key=lambda x: semantic_scores[x], reverse=True).index(idx) + 1
            rank_keyword = sorted(keyword_scores.keys(), key=lambda x: keyword_scores[x], reverse=True).index(idx) + 1
            rrf_scores[idx] = (1.0 / (k + rank_semantic)) + (1.0 / (k + rank_keyword))

        ranked_indices = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)[:limit]
        
        results = []
        for idx in ranked_indices:
            item = evidence[idx]
            if hasattr(item, 'confidence'):
                item.confidence = min(1.0, getattr(item, 'confidence', 0.5) + (rrf_scores[idx] * 0.1))
            results.append(item)

        return results

retriever = Retriever()