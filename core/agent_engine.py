from core.task import Task
from agent.planner import create_plan
from agent.brain import decide
from tools.registry import get
from core.logger import logger
from core.project_manager import project_manager
from core.research_memory import research_memory
from core.retry import retry
from core.profiler import profiler
from core.context import AgentContext
from core.telemetry import telemetry
from core.citation import citation_engine
from core.events import (
    AgentEvent, PlanningStarted, PlanningCompleted, SubGoalStarted,
    ToolStarted, ToolCompleted, WriterStarted, WriterCompleted, 
    Finished, Error, SearchCompleted, CrawlProgress, ExtractionProgress, MergeCompleted
)
from core.learning import learning_engine
from core.plugin_manager import plugin_manager
from core.checkpoint import checkpoint_manager
from config.settings import settings

# Register all tools (Triggers decorators for PluginManager)
import tools.strategy_tool
import tools.search_tool
import tools.crawler_tool
import tools.extractor_tool
import tools.merge_tool
import tools.validator_tool
import tools.kg_builder
import tools.review_tool
import tools.writer_tool

class AgentEngine:
    def run_stream(self, task: Task):
        context = AgentContext()
        
        # Telemetry & Orchestration Init
        telemetry.reset()
        telemetry.record("orchestration", "start", {"goal": task.goal})
        
        # Production Architecture: Initialize Plugins & Health Checks
        plugin_manager.discover_plugins(settings.plugin_dirs)
        plugin_manager.run_health_check()

        # 1. Hierarchical Planning
        yield PlanningStarted(query=task.user_request)
        try:
            plan = create_plan(task.user_request, context)
            task.goal = plan.get("goal", task.user_request)
            task.task_type = plan.get("task_type", "general")
            task.expected_output = plan.get("expected_output", "report")
            task.evidence_sufficiency_threshold = plan.get("evidence_sufficiency_threshold", 0.85)
            task.sub_goals = plan.get("sub_goals", [{"id": "1", "description": task.user_request, "search_queries": [task.user_request], "required_tools": ["search", "crawl", "extract"]}])
            task.tools = plan.get("tools", ["search", "crawl", "extract", "merge", "validate", "build_kg", "review", "write", "finish"])
            yield PlanningCompleted(sub_goal_count=len(task.sub_goals), tools_assigned=task.tools)
        except Exception as e:
            yield Error(message=f"Planning failed: {str(e)}")
            return task

        # 2. Initialize State
        task.documents, task.search_results, task.extracted_data = [], [], []
        task.research_corpus, task.visited_urls, task.data, task.final_answer = "", set(), {}, ""
        task.current_step, task.thoughts, task.action_history, task.current_sub_goal_index = 0, [], [], 0

        # 3. Load Research Memory
        if task.use_memory:
            project = task.project_name.strip() or task.goal.lower().replace(" ", "_").replace("/", "_")
            task.project_name = project
            previous = research_memory.load(project)
            task.loaded_memory, task.memory_hits = previous, len(previous)
            for evidence in previous:
                evidence.metadata = getattr(evidence, "metadata", {})
                evidence.metadata["from_memory"] = True
                context.evidence_store.add(evidence)

        logger.log(f"RESEARCH OS: Main Goal: {task.goal} | Sub-goals: {len(task.sub_goals)}")

        # 4. Main Hierarchical Loop (Using Centralized Settings)
        max_steps_per_subgoal = settings.max_steps_per_subgoal
        global_max_steps = settings.global_max_steps
        global_step_count = 0

            # The loop continues as long as the Cognitive State is not satisfied 
            # and we haven't hit the hard global step limit.
        while not context.cognitive_state.is_satisfied() and global_step_count < global_max_steps:
            current_sub = task.sub_goals[task.current_sub_goal_index]
            yield SubGoalStarted(sub_goal_index=task.current_sub_goal_index, description=current_sub.get('description'))
            
            if not task.search_results or task.current_step == 0:
                task.search_queries = current_sub.get("search_queries", [current_sub.get("description")])

            local_step = 0
            while local_step < max_steps_per_subgoal and global_step_count < global_max_steps:
                global_step_count += 1
                local_step += 1
                task.current_step += 1

                try:
                    decision = decide(task, context)
                except Exception as e:
                    yield Error(message=f"Brain error: {str(e)}")
                    break

                thought, tool_name = decision.get("thought", ""), decision.get("tool", "finish")
                task.thoughts.append(thought)

                if tool_name == "finish":
                    break

                if tool_name not in task.tools:
                    tool_name = "search"

                yield ToolStarted(tool_name=tool_name, step=task.current_step)
                initial_evidence_count = len(task.extracted_data)

                try:
                    tool = get(tool_name)
                        # If the brain chose to strategize, execute it and immediately chain to search
                    if tool_name == "strategize":
                            retry(tool.run, task, context)
                            # Chain to search immediately using the newly generated queries
                            tool_name = "search"
                            tool = get("search")
                            profiler.start(tool_name)
                    profiler.start(tool_name)
                    
                    # Yield specific tool progress events based on tool type
                    if tool_name == "search":
                        try:
                            retry(tool.run, task, context)
                            yield SearchCompleted(results_count=len(task.search_results))
                        except Exception as e:
                            yield Error(message=f"Search failed: {str(e)}", tool_name=tool_name)
                    elif tool_name == "crawl":
                        try:
                            retry(tool.run, task, context)
                            yield CrawlProgress(urls_visited=len(task.visited_urls), documents_extracted=len(task.documents))
                        except Exception as e:
                            yield Error(message=f"Crawl failed: {str(e)}", tool_name=tool_name)
                    elif tool_name == "extract":
                        try:
                            retry(tool.run, task, context)
                            yield ExtractionProgress(new_facts=len(task.extracted_data) - initial_evidence_count, total_facts=len(task.extracted_data))
                        except Exception as e:
                            yield Error(message=f"Extract failed: {str(e)}", tool_name=tool_name)
                    elif tool_name == "merge":
                        try:
                            retry(tool.run, task, context)
                            yield MergeCompleted(corpus_size=len(task.research_corpus))
                        except Exception as e:
                            yield Error(message=f"Merge failed: {str(e)}", tool_name=tool_name)
                    else:
                        retry(tool.run, task, context)

                    elapsed = profiler.stop(tool_name)
                    evidence_delta = len(task.extracted_data) - initial_evidence_count
                    
                    task.action_history.append({
                        "step": task.current_step, "sub_goal": task.current_sub_goal_index + 1,
                        "tool": tool_name, "time": round(elapsed, 2),
                        "documents": len(task.documents), "evidence_items": len(task.extracted_data)
                    })
                    
                    yield ToolCompleted(tool_name=tool_name, duration_ms=elapsed * 1000, evidence_delta=evidence_delta)
                    
                    telemetry.record("tool_execution", "tool_complete", {
                        "tool_name": tool_name, 
                        "status": "success",
                        "evidence_delta": evidence_delta
                    }, duration_ms=elapsed * 1000)

                    # Production Architecture: Robust Checkpointing after every successful tool
                    try:
                        checkpoint_manager.save(
                            project_id=task.project_name or "default",
                            task_state={
                                "goal": task.goal,
                                "current_step": task.current_step,
                                "current_sub_goal_index": task.current_sub_goal_index,
                                "extracted_data_count": len(task.extracted_data),
                                "documents_count": len(task.documents),
                                "final_answer": task.final_answer
                            },
                            stage=tool_name
                        )
                    except Exception:
                        pass  # Fault isolation: Do not crash the pipeline if checkpointing fails
                        
                except Exception as e:
                    profiler.stop(tool_name)
                    yield Error(message=f"Tool execution failed ({tool_name}): {str(e)}", tool_name=tool_name)
                    break

            task.current_sub_goal_index += 1

        # 5. Final Write Phase
        if "write" in task.tools and not task.final_answer:
            yield WriterStarted()
            try:
                tool = get("write")
                profiler.start("write")
                retry(tool.run, task, context)
                profiler.stop("write")
                yield WriterCompleted(report_length=len(task.final_answer))
            except Exception as e:
                profiler.stop("write")
                yield Error(message=f"Write failed: {str(e)}", tool_name="write")

        # 6. Persistence & Learning
        try:
            project_manager.save(task)
            if task.use_memory and task.project_name:
                research_memory.save(task.project_name, context.evidence_store.all())
                
            # Persist Autonomous Learning State
            try:
                learning_engine.save()
                logger.log("Learning state persisted successfully.")
            except Exception as e:
                logger.log(f"Learning persistence error: {e}")
                
        except Exception as e:
            yield Error(message=f"Persistence error: {str(e)}")

        # Final Telemetry & Completion
        final_confidence = task.data.get("review_score", 0.0)
        telemetry.record("orchestration", "finish", {"final_confidence": final_confidence})
        
        yield Finished(total_steps=task.current_step, final_confidence=final_confidence)
        return task

    def run(self, task: Task) -> Task:
        """Synchronous wrapper that consumes the stream and returns the final Task."""
        final_task = None
        for event in self.run_stream(task):
            if isinstance(event, Finished) or isinstance(event, Error):
                final_task = task
        return final_task if final_task is not None else task

agent_engine = AgentEngine()