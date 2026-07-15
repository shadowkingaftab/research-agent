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

# Register tools
import tools.search_tool
import tools.crawler_tool
import tools.extractor_tool
import tools.merge_tool
import tools.validator_tool
import tools.writer_tool


class AgentEngine:

    def run(self, task: Task):

        # -------------------------
        # Shared Context
        # -------------------------

        context = AgentContext()

        # -------------------------
        # Planning
        # -------------------------

        plan = create_plan(task.user_request)

        task.goal = plan.get("goal", task.user_request)
        task.task_type = plan.get("task_type", "general")
        task.expected_output = plan.get("expected_output", "answer")

        task.search_queries = plan.get(
            "search_queries",
            [task.user_request],
        )

        task.tools = plan.get(
            "tools",
            [
                "search",
                "crawl",
                "extract",
                "merge",
                "validate",
                "write",
                "finish",
            ],
        )

        if "write" not in task.tools:
            task.tools.append("write")

        if "finish" not in task.tools:
            task.tools.append("finish")

        # -------------------------
        # Initialize State
        # -------------------------

        task.documents = []
        task.search_results = []
        task.extracted_data = []
        task.research_corpus = ""
        task.visited_urls = set()

        task.data = {}
        task.final_answer = ""

        task.current_step = 0
        task.thoughts = []
        task.action_history = []

        # -------------------------
        # Load Research Memory
        # -------------------------

        if task.use_memory:

            project = task.project_name.strip() or task.goal.lower().replace(" ", "_")

            task.project_name = project

            previous = research_memory.load(project)

            task.loaded_memory = previous
            task.memory_hits = len(previous)

            for evidence in previous:
                evidence.metadata["from_memory"] = True
                context.evidence_store.add(evidence)

        logger.log("=" * 60)
        logger.log("AUTONOMOUS RESEARCH AGENT")
        logger.log("=" * 60)
        logger.log(f"Goal: {task.goal}")
        logger.log(f"Loaded Memories: {task.memory_hits}")

        # -------------------------
        # Main Agent Loop
        # -------------------------

        max_steps = 20

        for _ in range(max_steps):

            logger.log("")
            logger.log(f"STEP {task.current_step + 1}")

            try:

                decision = decide(task)

            except Exception as e:

                logger.log(f"Brain Error: {e}")
                break

            thought = decision.get("thought", "")
            tool_name = decision.get("tool", "finish")

            task.thoughts.append(thought)

            logger.log(f"Thought : {thought}")
            logger.log(f"Action  : {tool_name}")

            if tool_name == "finish":

                logger.log("Brain decided research is complete.")
                break

            if tool_name not in task.tools:

                logger.log(f"Unknown Tool: {tool_name}")
                break

            try:

                tool = get(tool_name)

                profiler.start(tool_name)

                try:

                    retry(tool.run, task, context)

                finally:

                    elapsed = profiler.stop(tool_name)

                task.current_step += 1

                task.action_history.append(
                    {
                        "step": task.current_step,
                        "tool": tool_name,
                        "time": round(elapsed, 2),
                        "documents": len(task.documents),
                        "search_results": len(task.search_results),
                        "extracted_items": (
                            len(task.extracted_data)
                            if isinstance(task.extracted_data, list)
                            else 1
                        ),
                    }
                )

                logger.log(
                    f"Finished {tool_name} in {elapsed:.2f}s"
                )

            except Exception as e:

                logger.log(
                    f"Tool Error ({tool_name}): {e}"
                )

                break

        # -------------------------
        # Save Project
        # -------------------------

        try:

            project_path = project_manager.save(task)

            logger.log(f"Project Saved: {project_path}")

        except Exception as e:

            logger.log(f"Project Save Error: {e}")

        # -------------------------
        # Save Memory
        # -------------------------

        # -------------------------
        # Save Research Memory
        # -------------------------

        try:

            if task.use_memory and task.project_name:

                research_memory.save(task.project_name, context.evidence_store.all())

                task.research_statistics = {
                    "documents": context.document_store.count(),
                    "evidence_total": context.evidence_store.count(),
                    "evidence_by_category": context.evidence_store.summary()["categories"],
                    "memory_hits": task.memory_hits,
                }

                logger.log(
                    f"Memory Updated ({context.evidence_store.count()} evidence)"
                )

        except Exception as e:

            logger.log(f"Memory Save Error: {e}")

        # -------------------------
        # Final Answer
        # -------------------------

        logger.log("")
        logger.log("=" * 60)
        logger.log("FINAL ANSWER")
        logger.log("=" * 60)

        if task.final_answer:

            print(task.final_answer)

        else:

            print("No final answer generated.")

        # -------------------------
        # Session Summary
        # -------------------------

        logger.log("")
        logger.log("=" * 60)
        logger.log("SESSION SUMMARY")
        logger.log("=" * 60)

        logger.log(f"Steps Executed : {task.current_step}")
        logger.log(f"Documents      : {len(task.documents)}")
        logger.log(f"Search Results : {len(task.search_results)}")

        if isinstance(task.extracted_data, list):

            logger.log(
                f"Extractions    : {len(task.extracted_data)}"
            )

        else:

            logger.log("Extractions    : 1")

        total_time = sum(
            step.get("time", 0)
            for step in task.action_history
        )

        logger.log(f"Total Tool Time: {total_time:.2f}s")

        logger.log("")
        logger.log("Tool Performance")

        for step in task.action_history:

            logger.log(
                f"Step {step['step']:02d} | "
                f"{step['tool']:<10} | "
                f"{step['time']:.2f}s"
            )

        logger.log("")
        logger.log("=" * 60)
        logger.log("AGENT FINISHED")
        logger.log("=" * 60)

        return task


agent_engine = AgentEngine()