from core.agent_engine import agent_engine
from core.task import Task


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
    main()