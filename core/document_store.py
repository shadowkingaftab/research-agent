from typing import Dict, List

from models.document import Document


class DocumentStore:

    def __init__(self):
        self.clear()

    def clear(self):
        self._documents: List[Document] = []
        self._url_index: Dict[str, Document] = {}

    def add(self, document: Document) -> bool:
        """
        Adds a document if its URL is not already present.
        Returns True if added, False if duplicate.
        """
        url = document.source.url

        if url in self._url_index:
            return False

        self._documents.append(document)
        self._url_index[url] = document

        return True

    def exists(self, url: str) -> bool:
        return url in self._url_index

    def get(self, url: str):
        return self._url_index.get(url)

    def remove(self, url: str):
        doc = self._url_index.pop(url, None)

        if doc:
            self._documents.remove(doc)

    def all(self) -> List[Document]:
        return list(self._documents)

    def count(self) -> int:
        return len(self._documents)

    def urls(self):
        return list(self._url_index.keys())
    
    def search(self, text: str):

        text = text.lower()

        results = []

        for document in self._documents:

            title = getattr(document, "title", "")

            if hasattr(document, "source"):
                title = getattr(document.source, "title", title)

            content = getattr(document, "content", "")

            if (
                text in title.lower()
                or text in content.lower()
           ):
                results.append(document)

        return results


    def latest(self, limit: int = 10):

        return self._documents[-limit:]


    def domains(self):

        domains = {}

        for document in self._documents:

            try:

                url = document.source.url

                domain = url.split("/")[2]

                domains.setdefault(domain, 0)

                domains[domain] += 1

            except Exception:

                continue

        return domains


    def stats(self):

        return {
            "documents": len(self._documents),
            "domains": len(self.domains()),
        }