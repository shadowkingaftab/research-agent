import os
import json
import hashlib
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Set, Any
from core.logger import logger

@dataclass
class Entity:
    canonical_id: str
    name: str
    entity_type: str
    aliases: Set[str] = field(default_factory=set)
    confidence: float = 0.5
    evidence_ids: List[str] = field(default_factory=list)
    project_ids: Set[str] = field(default_factory=set)

    def to_dict(self):
        d = asdict(self)
        d['aliases'] = list(self.aliases)
        d['project_ids'] = list(self.project_ids)
        return d

    @classmethod
    def from_dict(cls, data):
        data['aliases'] = set(data.get('aliases', []))
        data['project_ids'] = set(data.get('project_ids', []))
        return cls(**data)

@dataclass
class Relationship:
    source_id: str
    target_id: str
    relation_type: str
    confidence: float = 0.5
    evidence_ids: List[str] = field(default_factory=list)
    project_ids: Set[str] = field(default_factory=set)
    temporal_context: str = ""

    def to_dict(self):
        d = asdict(self)
        d['project_ids'] = list(self.project_ids)
        return d

    @classmethod
    def from_dict(cls, data):
        data['project_ids'] = set(data.get('project_ids', []))
        return cls(**data)

class AdvancedKnowledgeGraph:
    def __init__(self, base_dir: str = "./workspace/knowledge_graphs"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
        self.entities: Dict[str, Entity] = {}
        self.relationships: List[Relationship] = []

    def _generate_canonical_id(self, name: str, entity_type: str) -> str:
        normalized = name.lower().strip()
        return hashlib.sha256(f"{normalized}|{entity_type}".encode()).hexdigest()[:12]

    def _normalize_name(self, name: str) -> str:
        return name.strip().title()

    def resolve_or_create_entity(self, name: str, entity_type: str, aliases: List[str] = None, 
                                 confidence: float = 0.5, evidence_ids: List[str] = None, project_id: str = "") -> str:
        normalized_name = self._normalize_name(name)
        cid = self._generate_canonical_id(normalized_name, entity_type)
        
        if cid in self.entities:
            entity = self.entities[cid]
            entity.confidence = max(entity.confidence, confidence)
            if evidence_ids:
                entity.evidence_ids.extend([e for e in evidence_ids if e not in entity.evidence_ids])
            if project_id:
                entity.project_ids.add(project_id)
            if aliases:
                entity.aliases.update([self._normalize_name(a) for a in aliases])
        else:
            self.entities[cid] = Entity(
                canonical_id=cid,
                name=normalized_name,
                entity_type=entity_type,
                aliases=set([self._normalize_name(a) for a in aliases] if aliases else []),
                confidence=confidence,
                evidence_ids=evidence_ids or [],
                project_ids=set([project_id] if project_id else [])
            )
        return cid

    def add_relationship(self, source_name: str, target_name: str, relation_type: str, 
                         entity_type: str = "Concept", confidence: float = 0.5, 
                         evidence_ids: List[str] = None, project_id: str = "", temporal: str = ""):
        source_id = self.resolve_or_create_entity(source_name, entity_type, project_id=project_id)
        target_id = self.resolve_or_create_entity(target_name, entity_type, project_id=project_id)
        
        for rel in self.relationships:
            if rel.source_id == source_id and rel.target_id == target_id and rel.relation_type == relation_type:
                rel.confidence = max(rel.confidence, confidence)
                if evidence_ids:
                    rel.evidence_ids.extend([e for e in evidence_ids if e not in rel.evidence_ids])
                if project_id:
                    rel.project_ids.add(project_id)
                return

        self.relationships.append(Relationship(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            confidence=confidence,
            evidence_ids=evidence_ids or [],
            project_ids=set([project_id] if project_id else []),
            temporal_context=temporal
        ))

    def query_entities(self, name: str = None, entity_type: str = None) -> List[Entity]:
        results = []
        for entity in self.entities.values():
            if name and name.lower() not in entity.name.lower() and not any(name.lower() in a.lower() for a in entity.aliases):
                continue
            if entity_type and entity.entity_type != entity_type:
                continue
            results.append(entity)
        return results

    def query_relationships(self, entity_id: str = None, relation_type: str = None) -> List[Relationship]:
        results = []
        for rel in self.relationships:
            if entity_id and rel.source_id != entity_id and rel.target_id != entity_id:
                continue
            if relation_type and rel.relation_type != relation_type:
                continue
            results.append(rel)
        return results

    def to_mermaid(self, limit: int = 50) -> str:
        lines = ["graph TD"]
        sorted_rels = sorted(self.relationships, key=lambda r: r.confidence, reverse=True)[:limit]
        for rel in sorted_rels:
            if rel.source_id in self.entities and rel.target_id in self.entities:
                src_name = self.entities[rel.source_id].name.replace(" ", "_")
                tgt_name = self.entities[rel.target_id].name.replace(" ", "_")
                lines.append(f"  {src_name} -->|{rel.relation_type}| {tgt_name}")
        return "\n".join(lines) if len(lines) > 1 else ""

    def save(self, project_id: str):
        if not project_id:
            return
        filepath = os.path.join(self.base_dir, f"{project_id}.json")
        data = {
            "entities": {k: v.to_dict() for k, v in self.entities.items()},
            "relationships": [r.to_dict() for r in self.relationships]
        }
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.log(f"Failed to save KG for {project_id}: {e}")

    def load(self, project_id: str):
        if not project_id:
            return
        filepath = os.path.join(self.base_dir, f"{project_id}.json")
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                self.entities = {k: Entity.from_dict(v) for k, v in data.get("entities", {}).items()}
                self.relationships = [Relationship.from_dict(r) for r in data.get("relationships", [])]
            except Exception as e:
                logger.log(f"Failed to load KG for {project_id}: {e}")

advanced_kg = AdvancedKnowledgeGraph()