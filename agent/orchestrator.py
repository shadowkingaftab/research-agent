from core.logger import logger
from core.task import Task
from agent.planner import create_plan
from agent.brain import decide
from tools.registry import get
from core.telemetry import telemetry
from core.citation import citation_engine

class Orchestrator:
    def execute(self, task: Task):
        logger.log("🚀 Orchestrator: Initiating multi-agent execution sequence.")
        telemetry.record("orchestration", "start", {"goal": task.goal})
        
        # Phase 1: Planning
        telemetry.record("orchestration", "phase_start", {"phase": "planning"})
        plan = create_plan(task.user_request)
        task.goal = plan.get("goal", task.user_request)
        task.sub_goals = plan.get("sub_goals", [])
        task.tools = plan.get("tools", [])
        telemetry.record("orchestration", "phase_end", {"phase": "planning", "sub_goals": len(task.sub_goals)})

        # Phase 2: Iterative Research & Verification
        telemetry.record("orchestration", "phase_start", {"phase": "research_and_verify"})
        for idx, sub_goal in enumerate(task.sub_goals):
            task.current_sub_goal_index = idx
            logger.log(f"▶ Orchestrator: Executing sub-goal {idx + 1}/{len(task.sub_goals)}")
            
            # Researcher Agent Loop
            local_step = 0
            while local_step < 15:
                local_step += 1
                decision = decide(task)
                tool_name = decision.get("tool", "finish")
                
                if tool_name == "finish":
                    break
                    
                try:
                    tool = get(tool_name)
                    tool.run(task, None) # Context simplified for orchestration layer
                    telemetry.record("tool_execution", "complete", {"tool": tool_name})
                except Exception as e:
                    logger.log(f"Tool execution failed: {e}")
                    
        telemetry.record("orchestration", "phase_end", {"phase": "research_and_verify"})

        # Phase 3: Synthesis & Writing
        telemetry.record("orchestration", "phase_start", {"phase": "writing"})
        try:
            writer = get("write")
            writer.run(task, None)
        except Exception as e:
            logger.log(f"Writer agent failed: {e}")
        telemetry.record("orchestration", "phase_end", {"phase": "writing"})

        telemetry.record("orchestration", "complete", {"final_confidence": task.data.get("review_score", 0.0)})
        return task

orchestrator = Orchestrator()