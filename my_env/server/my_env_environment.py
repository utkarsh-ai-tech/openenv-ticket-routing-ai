from fastapi import FastAPI
from my_env.models import Action, Observation
from my_env.tasks import TASKS
from my_env.grader import grade
from my_env.reward import compute_reward

app = FastAPI()

class MyEnv:
    def __init__(self):
        self.current_task = None
        self.done = False 

    def reset(self, task_id=1):
        self.current_task = TASKS[task_id - 1]
        self.done = False
        return Observation(
            ticket_id=self.current_task["id"],
            message=self.current_task["ticket"]
        )

    def step(self, action: Action):
        expected = self.current_task["expected"]

        score = grade(action, expected)
        reward = compute_reward(score)

        self.done = True

        return (
            Observation(ticket_id=self.current_task["id"], message="Processed"),
            reward,
            self.done,
            {"score": score}
        )

    def state(self):
        return self.current_task


env = MyEnv()

from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head>
            <title>OpenEnv Ticket Routing AI</title>
        </head>
        <body style="background:black; color:white; text-align:center; padding:50px;">
            <h1>🚀 OpenEnv Ticket Routing AI</h1>
            <p>Real-world AI customer support simulation</p>

            <h2>🔗 Links</h2>
            <a href="/docs">👉 API Docs</a><br><br>
            <a href="/tasks">👉 View Tasks</a><br><br>
            <a href="/baseline">👉 Baseline Score</a><br><br>
            <a href="/health">👉 Health Check</a>

            <p style="margin-top:40px;">Built by Utkarsh 😎</p>
        </body>
    </html>
    """

@app.get("/reset")
def reset(task_id: int = 1):
    obs = env.reset(task_id)
    return obs.model_dump()

@app.post("/step")
def step(action: Action):
    obs, reward, done, info = env.step(action)
    return {
        "observation": obs.model_dump(),
        "reward": reward,
        "done": done,
        "info": info
    }

@app.get("/state")
def state():
    return env.state()

@app.get("/baseline")
def baseline():
    scores = []
    for i in range(1, 4):
        env.reset(i)
        action = Action(
            category="billing",
            priority="medium",
            response="Checking issue",
            escalate=False
        )
        _, _, _, info = env.step(action)
        scores.append(info["score"])

    return {"baseline_score": sum(scores) / len(scores)}

@app.get("/tasks")
def get_tasks():
    return [
        {
            "id": t["id"],
            "difficulty": t["difficulty"],
            "ticket": t["ticket"]
        }
        for t in TASKS
    ]

@app.get("/grader")
def get_grader():
    if env.current_task is None:
        return {"error": "No task running"}

    return {
        "task_id": env.current_task["id"],
        "expected": env.current_task["expected"]
    }

@app.get("/health")
def health():
    return {"status": "ok"}