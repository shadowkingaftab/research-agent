from urllib.parse import urlparse


class EvidenceRanker:

    TRUSTED_DOMAINS = {
        "openai.com": 1.0,
        "deepmind.google": 1.0,
        "google.com": 0.95,
        "microsoft.com": 0.95,
        "github.com": 0.90,
        "arxiv.org": 0.95,
        "nature.com": 1.0,
        "ieee.org": 1.0,
        "acm.org": 1.0,
        "wikipedia.org": 0.75,
    }

    def rank(self, evidence):

        url = evidence.get("source", "")

        try:
            domain = urlparse(url).netloc.lower()
        except Exception:
            domain = ""

        confidence = 0.50

        for trusted, score in self.TRUSTED_DOMAINS.items():

            if trusted in domain:
                confidence = score
                break

        evidence["domain"] = domain
        evidence["confidence"] = confidence
        evidence["citations"] = 1
        evidence["verified"] = False

        return evidence


ranker = EvidenceRanker()