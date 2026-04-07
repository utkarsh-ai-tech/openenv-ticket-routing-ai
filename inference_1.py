import sys
import threading
import requests
import time
from server.app import app  # ✅ Dockerfile ka "inference:app" kaam karega

BASE_URL = "http://localhost:7860"

def run_episode():
    time.sleep(3)  # Server start hone do pehle
    
    from my_env.tasks import TASKS
    from my_env.models import Action
    import random
    
    for i in range(1, len(TASKS) + 1):
        task_name = f"ticket-routing-{i}"
        
        # Reset
        res = requests.post(f"{BASE_URL}/reset", json={"task_id": i})
        data = res.json()
        
        print(f"[START] task={task_name}", flush=True)
        
        # Action
        action = {
            "category": random.choice(["billing", "tech", "complaint"]),
            "priority": random.choice(["low", "medium", "high"]),
            "response": "Processing ticket",
            "escalate": False
        }
        
        res = requests.post(f"{BASE_URL}/step", json=action)
        result = res.json()
        
        reward = result.get("reward", 0)
        score = result.get("info", {}).get("score", reward)
        
        print(f"[STEP] step=1 reward={reward}", flush=True)
        print(f"[END] task={task_name} score={score} steps=1", flush=True)

# Background thread mein episode run karo
thread = threading.Thread(target=run_episode, daemon=True)
thread.start()
