from core.task import Task

from agent.planner import create_plan
from agent.brain import decide

from tools.registry import get
from core.logger import logger

# Register tools
import tools.search_tool
import tools.crawler_tool
import tools.extractor_tool
import tools.merge_tool
import tools.validator_tool
import tools.writer_tool

try:
    from core.project_manager import projects
    HAS_PROJECTS = True
except Exception:
    HAS_PROJECTS = False


class AgentEngine:

    def run(self, task: Task):

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

        task.tools = [
            "search",
            "crawl",
            "extract",
            "merge",
            "validate",
            "write",
            "finish",
        ]

        # -------------------------
        # Initialize task state
        # -------------------------

        task.documents = []
        task.search_results = []
        task.extracted_data = []
        task.research_corpus = ""
        task.visited_urls = set()

        task.data = {}
        task.final_answer = ""

        task.thoughts = []
        task.action_history = []
        task.current_step = 0

        print("\n========================================")
        print("AUTONOMOUS RESEARCH AGENT")
        print("========================================")
        print("Goal:", task.goal)

        max_steps = 20

        for _ in range(max_steps):

            print(f"\n========== STEP {task.current_step + 1} ==========")

            try:

                decision = decide(task)

            except Exception as e:

                print("Brain Error:", e)
                break

            thought = decision.get("thought", "")
            tool_name = decision.get("tool", "finish")

            task.thoughts.append(thought)

            logger.log(f"Thought: {thought}")
            logger.log(f"Action: {tool_name}")

            if tool_name == "finish":

                print("\nAgent decided the task is complete.")
                break

            if tool_name not in task.tools:

                print(f"\nUnknown tool: {tool_name}")
                break

            try:

                tool = get(tool_name)

                tool.run(task)

                task.current_step += 1

                task.action_history.append(
                    {
                        "step": task.current_step,
                        "tool": tool_name,
                        "documents": len(task.documents),
                        "search_results": len(task.search_results),
                        "extracted_items": (
                            len(task.extracted_data)
                            if isinstance(task.extracted_data, list)
                            else 1
                        ),
                    }
                )

                logger.log(f"Finished: {tool_name}")

            except Exception as e:

                print(f"Tool Error ({tool_name}): {e}")
                break

        # -------------------------
        # Save project
        # -------------------------

        if HAS_PROJECTS:

            try:

                projects.save("latest", task)

                logger.log("Project saved.")

            except Exception as e:

                print("Project Save Error:", e)

        # -------------------------
        # Final Output
        # -------------------------

        print("\n========================================")
        print("FINAL ANSWER")
        print("========================================")

        if task.final_answer:
            print(task.final_answer)
        else:
            print("No final answer generated.")

        print("\n========================================")
        print("SESSION SUMMARY")
        print("========================================")
        print("Steps Executed :", task.current_step)
        print("Documents      :", len(task.documents))
        print("Search Results :", len(task.search_results))

        if isinstance(task.extracted_data, list):
            print("Extractions    :", len(task.extracted_data))
        else:
            print("Extractions    : 1")

        print("\n========================================")
        print("AGENT FINISHED")
        print("========================================")

        return task


agent_engine = AgentEngine()