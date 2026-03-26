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

from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <head>
        <title>OpenEnv Ticket Routing AI</title>
        <style>
            body {
                margin: 0;
                font-family: 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #0f172a, #1e293b);
                color: white;
                text-align: center;
            }
            .container {
                padding: 50px;
            }
            h1 {
                font-size: 45px;
                color: #38bdf8;
                margin-bottom: 10px;
            }
            p {
                font-size: 18px;
                color: #cbd5f5;
            }
            .card {
                margin: 30px auto;
                padding: 25px;
                width: 60%;
                background: #1e293b;
                border-radius: 15px;
                box-shadow: 0px 10px 30px rgba(0,0,0,0.5);
                transition: transform 0.3s;
            }
            .card:hover {
                transform: scale(1.05);
            }
            a {
                display: inline-block;
                margin: 10px;
                padding: 12px 20px;
                background: #38bdf8;
                color: black;
                text-decoration: none;
                border-radius: 8px;
                font-weight: bold;
                transition: 0.3s;
            }
            a:hover {
                background: #0ea5e9;
                transform: scale(1.1);
            }
            .footer {
                margin-top: 40px;
                font-size: 14px;
                color: #94a3b8;
            }
        </style>
    </head>

    <body>
        <div class="container">
            <h1>🚀 OpenEnv Ticket Routing AI</h1>
            <p>Real-world AI Customer Support Simulation Environment</p>

            <div class="card">
                <h2>📘 Explore API</h2>
                <a href="/docs">API Docs</a>
                <a href="/tasks">View Tasks</a>
                <a href="/baseline">Baseline Score</a>
                <a href="/health">Health Check</a>
            </div>

            <div class="card">
                <h2>🧠 Features</h2>
                <p>✔ Multi-task environment (Easy → Hard)</p>
                <p>✔ Intelligent reward system</p>
                <p>✔ Real-world ticket classification</p>
                <p>✔ OpenEnv compatible API</p>
            </div>

            <div class="card">
                <h2>⚡ Quick Start</h2>
                <p>1. Go to API Docs</p>
                <p>2. Run /reset</p>
                <p>3. Try /step</p>
                <p>4. Check reward & score</p>
            </div>

            <div class="footer">
                Built with ❤️ by Utkarsh | OpenEnv Hackathon 🚀
            </div>
        </div>
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