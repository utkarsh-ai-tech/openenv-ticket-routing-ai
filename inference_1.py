import sys
import random
import threading
from my_env.tasks import TASKS
from my_env.models import Action
from my_env.grader import grade
from my_env.reward import compute_reward
from server.app import app  # ✅ uvicorn ke liye

def run_episode():
    for i in range(1, len(TASKS) + 1):
        task = TASKS[i - 1]
        task_name = f"ticket-routing-{i}"

        print(f"[START] task={task_name}", flush=True)

        action = Action(
            category=random.choice(["billing", "tech", "complaint"]),
            priority=random.choice(["low", "medium", "high"]),
            response="Processing ticket",
            escalate=False
        )

        score = grade(action, task["expected"])
        reward = compute_reward(score)

        print(f"[STEP] step=1 reward={reward}", flush=True)
        print(f"[END] task={task_name} score={score} steps=1", flush=True)

# Startup pe episode run karo
run_episode()
