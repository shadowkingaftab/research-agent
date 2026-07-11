from core.task import Task
from agent.planner import create_plan

from tools.registry import get

from core.logger import logger
from core.context import AgentContext
from core.research_memory import research_memory

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
        # ---------------------------------
        # Load Research Memory
        # ---------------------------------

        if task.use_memory:

            project = task.project_name.strip()

            if not project:

                project = (
                    task.goal
                    .lower()
                    .replace(" ", "_")
                )

                task.project_name = project

            previous = research_memory.load(project)

            task.loaded_memory = previous

            task.memory_hits = len(previous)

            for evidence in previous:

                context.evidence_store.add(evidence)

            logger.log(
                f"Loaded {len(previous)} evidence from memory."
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
        if task.use_memory:

            project = task.project_name.strip()

            if not project:

                project = (
                    task.goal
                    .lower()
                    .replace(" ", "_")
                )

                task.project_name = project

            previous = research_memory.load(project)

            task.loaded_memory = previous

            task.memory_hits = len(previous)

            for evidence in previous:

                context.evidence_store.add(evidence)

            logger.log(
                f"Loaded {len(previous)} evidence from memory."
            )

        logger.log("==============================")
        logger.log("RESEARCH PLAN")
        logger.log("==============================")
        logger.log(str(plan))

        # -------------------------
        # Initialize Task
        # -------------------------

        task.documents = []
        task.search_results = []
        task.visited_urls = set()
        task.extracted_data = []
        task.research_corpus = ""

        max_iterations = 3

        # -------------------------
        # Research Loop
        # -------------------------

        for iteration in range(max_iterations):

            logger.log(
                f"========== Research Round {iteration + 1} =========="
            )

            # Temporary search results only
            task.search_results = []

            # -------------------------
            # Search + Crawl
            # -------------------------

            for tool_name in ("search", "crawl"):

                if tool_name not in task.tools:
                    continue

                logger.log(f"Running Tool: {tool_name}")

                tool = get(tool_name)

                tool.run(task, context)

            # -------------------------
            # Rebuild Research Corpus
            # -------------------------

            

            # -------------------------
            # Extract
            # -------------------------

            if "extract" in task.tools:

                logger.log("Running Tool: extract")

                get("extract").run(task, context)

            # -------------------------
            # Validate
            # -------------------------

            if "validate" in task.tools:

                logger.log("Running Tool: validate")

                get("validate").run(task, context)

            evaluation = task.data.get("evaluation")

            if evaluation is None:
                logger.log("Validator returned no evaluation.")
                break

            if evaluation.get("enough_information", False):

                logger.log("Research complete.")

                break

            new_queries = evaluation.get(
                "next_search_queries",
                [],
            )

            if not new_queries:

                logger.log("No additional search queries.")

                break

            logger.log("Need another research round.")

            task.search_queries = new_queries

        # -------------------------
        # Merge
        # -------------------------

        if "merge" in task.tools:

            logger.log("Running Merge Tool...")

            get("merge").run(task, context)

        # -------------------------
        # Writer
        # -------------------------

        if "write" in task.tools:

            logger.log("Running Writer Tool...")

            get("write").run(task, context)

        logger.log("==============================")
        logger.log("ENGINE FINISHED")
        logger.log("==============================")

        return task


engine = Engine()