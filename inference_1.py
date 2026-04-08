import os
import json
from openai import OpenAI
from my_env.tasks import TASKS
from my_env.models import Action
from my_env.grader import grade
from my_env.reward import compute_reward
from server.app import app  # uvicorn ke liye

def run_episode():
    # Client andar banao - bahar banane se Space crash karega
    api_base = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
    api_key = os.environ.get("API_KEY", "dummy-key")
    
    client = OpenAI(base_url=api_base, api_key=api_key)

    for i in range(1, len(TASKS) + 1):
        task = TASKS[i - 1]
        task_name = f"ticket-routing-{i}"

        print(f"[START] task={task_name}", flush=True)

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a ticket routing AI. Given a support ticket, respond in JSON:
{"category": "billing" or "tech" or "complaint", "priority": "low" or "medium" or "high", "response": "brief response", "escalate": true or false}
Only respond with JSON, nothing else."""
                    },
                    {"role": "user", "content": f"Route this ticket: {task['ticket']}"}
                ]
            )
            data = json.loads(response.choices[0].message.content.strip())
            action = Action(**data)
        except Exception as e:
            print(f"LLM error: {e}", flush=True)
            action = Action(
                category="tech",
                priority="medium", 
                response="Processing ticket",
                escalate=False
            )

        score = grade(action, task["expected"])
        reward = compute_reward(score)

        print(f"[STEP] step=1 reward={reward}", flush=True)
        print(f"[END] task={task_name} score={score} steps=1", flush=True)

run_episode()
