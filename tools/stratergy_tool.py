from tools.base import Tool
from tools.registry import register
from core.search_strategy import SearchStrategyEngine
from core.logger import logger

class StrategyTool(Tool):
    name = "strategize"

    def run(self, task, context):
        logger.log("Strategy Engine: Evaluating cognitive state and formulating search trajectory...")
        
        engine = SearchStrategyEngine()
        queries = engine.evaluate_and_adapt(task, context)
        
        # Inject the generated queries back into the task for the search tool to consume
        task.search_queries = queries
        
        logger.log(f"Strategy Engine: Injected {len(queries)} queries into task pipeline.")
        return task

register(StrategyTool())