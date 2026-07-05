from core.task import Task
from agent.planner import create_plan

from tools.registry import get
from core.logger import logger

# Register tools
import tools.search_tool
import tools.crawler_tool
import tools.extractor_tool
import tools.validator_tool
import tools.merge_tool
import tools.writer_tool


class Engine:

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
            [task.user_request]
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
            ],
        )

        print("\n==============================")
        print("RESEARCH PLAN")
        print("==============================")
        print(plan)

        # Initialize persistent storage
        task.documents = []
        task.visited_urls = set()
        task.extracted_data = []

        max_iterations = 3

        for iteration in range(max_iterations):

            print(f"\n========== Research Round {iteration + 1} ==========")

            # Only clear temporary search results
            task.search_results = []

            # Run Search + Crawl
            for tool_name in ("search", "crawl"):

                if tool_name not in task.tools:
                    continue

                print(f"\nRunning Tool: {tool_name}")

                get(tool_name).run(task)

            # Rebuild corpus from ALL collected documents
            corpus = ""

            for doc in task.documents:

                corpus += f"""

TITLE:
{doc['title']}

URL:
{doc['url']}

CONTENT:
{doc['content'][:6000]}

"""

            task.research_corpus = corpus

            # Extract everything from accumulated corpus
            if "extract" in task.tools:

                logger.log("Running Tool: search")

                get("extract").run(task)

            # Validate
            if "validate" in task.tools:

                print("\nRunning Tool: validate")

                get("validate").run(task)

            evaluation = task.data.get("evaluation")

            if evaluation is None:
                break

            if evaluation.get("enough_information", False):
                logger.log("Research complete.")
                break

            new_queries = evaluation.get("next_search_queries", [])

            if not new_queries:
                print("\nNo additional search queries.")
                break

            logger.log("Need another research round.")

            task.search_queries = new_queries

        # Merge chunk extractions
        if "merge" in task.tools:

            print("\nRunning Merge Tool...")

            get("merge").run(task)

        # Final report
        if "write" in task.tools:

            print("\nRunning Writer Tool...")

            get("write").run(task)

        print("\n==============================")
        print("ENGINE FINISHED")
        print("==============================")

        return task


engine = Engine()