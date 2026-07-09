from urllib.parse import urlparse


class SourceRanker:

    DOMAIN_SCORES = {

        # Official

        ".gov": 1.00,
        ".edu": 0.97,
        ".ac.": 0.96,

        "openai.com": 0.98,
        "google.com": 0.98,
        "deepmind.com": 0.98,
        "anthropic.com": 0.98,
        "microsoft.com": 0.98,
        "nvidia.com": 0.98,

        "github.com": 0.94,

        "arxiv.org": 0.95,

        "wikipedia.org": 0.85,

        "medium.com": 0.60,

        "reddit.com": 0.45,

        "quora.com": 0.40,

        "linkedin.com": 0.75,
    }

    DEFAULT = 0.70

    def score(self, url: str):

        domain = urlparse(url).netloc.lower()

        for key, score in self.DOMAIN_SCORES.items():

            if key in domain:

                return score

        return self.DEFAULT


source_ranker = SourceRanker()