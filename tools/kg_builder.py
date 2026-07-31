from tools.base import Tool
from tools.registry import register
from core.llm import llm
from core.logger import logger
from core.knowledge_graph import advanced_kg

class KGBuilderTool(Tool):
    name = "build_kg"

    def run(self, task, context):
            logger.log("Generating Knowledge Graph from extracted evidence...")
            
            # Retrieve evidence from context or task
            evidence_list = []
            if context and hasattr(context, 'evidence_store'):
                evidence_list = context.evidence_store.all()
            else:
                evidence_list = getattr(task, "extracted_data", [])
                
            if not evidence_list:
                return task

            # Load existing persistent KG for this project
            project_id = getattr(task, "project_name", "") or "default"
            advanced_kg.load(project_id)

            facts_text = "\n".join([f"- {getattr(e, 'fact', '')} (Source: {getattr(e, 'source_url', 'N/A')})" for e in evidence_list[:30]])
            prompt = f"""You are a Knowledge Graph extraction engine.
    Extract entities and their relationships from the following research facts.

    Facts: {facts_text}

    Return ONLY valid JSON:
    {{
    "entities": [
        {{"name": "Entity Name", "type": "Person|Organization|Location|Concept|Technology", "aliases": ["alias1"]}}
    ],
    "relationships": [
        {{"source": "Entity1", "target": "Entity2", "relation": "Relationship Type"}}
    ]
    }}"""

            try:
                result = llm.generate_json(prompt)
                entities = result.get("entities", [])
                relationships = result.get("relationships", [])

                # Incrementally resolve and add entities
                for ent in entities:
                    name = ent.get("name", "")
                    e_type = ent.get("type", "Concept")
                    aliases = ent.get("aliases", [])
                    if name:
                        advanced_kg.resolve_or_create_entity(
                            name=name, 
                            entity_type=e_type, 
                            aliases=aliases,
                            project_id=project_id
                        )

                # Incrementally add relationships
                for rel in relationships:
                    src = rel.get("source", "")
                    tgt = rel.get("target", "")
                    rel_type = rel.get("relation", "related_to")
                    if src and tgt:
                        advanced_kg.add_relationship(
                            source_name=src,
                            target_name=tgt,
                            relation_type=rel_type,
                            project_id=project_id
                        )

                # Save the updated persistent KG
                advanced_kg.save(project_id)

                # Generate Mermaid graph for the UI (backward compatibility)
                task.data["knowledge_graph_mermaid"] = advanced_kg.to_mermaid()
                task.data["kg_entities"] = [e.name for e in advanced_kg.entities.values()]
                logger.log(f"Knowledge Graph updated. Total entities: {len(advanced_kg.entities)}, relationships: {len(advanced_kg.relationships)}")
                
            except Exception as e:
                logger.log(f"KG Builder Error: {e}")
                task.data["knowledge_graph_mermaid"] = advanced_kg.to_mermaid()
                
            return task

register(KGBuilderTool())