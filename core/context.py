from core.llm import llm
from core.cache import cache
from core.logger import logger
from core.memory import memory
from core.project_manager import project_manager
from core.profiler import profiler

from core.document_store import DocumentStore
from core.evidence_store import EvidenceStore


class AgentContext:

    def __init__(self):

        self.llm = llm
        self.cache = cache
        self.logger = logger
        self.memory = memory
        self.project_manager = project_manager
        self.profiler = profiler

        self.document_store = DocumentStore()
        self.evidence_store = EvidenceStore()

    def clear(self):

        self.document_store.clear()
        self.evidence_store.clear()