from core.task import Task
from core.agent_engine import agent_engine

task = Task(
    user_request="Find the top AI companies in Europe and write a report."
)

agent_engine.run(task)

print(task.final_answer)