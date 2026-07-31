from core.agent_engine import agent_engine
from core.task import Task
from core.workspace import workspace
from agent.orchestrator import orchestrator

def main():

    print("========================================")
    print("AUTONOMOUS RESEARCH AGENT")
    print("========================================")

    while True:

        request = input("\nResearch Request (or 'exit'): ").strip()

        if request.lower() in {"exit", "quit"}:
            break

        if not request:
            continue

        task = Task(user_request=request)

        agent_engine.run(task)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Research OS Entry Point")
    parser.add_argument("--query", type=str, required=True, help="The research query")
    parser.add_argument("--project-id", type=str, default=None, help="Existing project ID to resume")
    args = parser.parse_args()

    # Initialize or Resume Workspace
    if args.project_id:
        project = workspace.get_project(args.project_id)
        logger.log(f"Resuming existing project: {project.name}")
        # Note: Context restoration logic would load project.context_state into Task here
    else:
        project = workspace.create_project(args.query)

    # Initialize Task
    task = Task(user_request=args.query)
    task.project_name = project.name

    # Execute via Orchestrator
    try:
        final_task = orchestrator.execute(task)
        
        # Persist final state
        workspace.save_checkpoint(project.id, {
            "goal": final_task.goal,
            "status": "completed",
            "final_answer": final_task.final_answer
        })
        
        print("\n--- FINAL REPORT ---\n")
        print(final_task.final_answer)
        
    except Exception as e:
        logger.log(f"Critical execution failure: {e}")
        workspace.save_checkpoint(project.id, {"status": "failed", "error": str(e)})