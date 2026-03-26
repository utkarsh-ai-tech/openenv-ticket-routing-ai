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
        <style>
            body {
                margin: 0;
                font-family: 'Segoe UI';
                background: linear-gradient(-45deg, #020617, #0f172a, #1e293b, #020617);
                background-size: 400% 400%;
                animation: bg 10s ease infinite;
                color: white;
                text-align: center;
                padding: 80px;
            }

            @keyframes bg {
                0%{background-position:0% 50%;}
                50%{background-position:100% 50%;}
                100%{background-position:0% 50%;}
            }

            h1 {
                font-size: 50px;
                color: #38bdf8;
                animation: fade 1.5s ease;
            }

            p {
                color: #94a3b8;
                margin-bottom: 40px;
            }

            @keyframes fade {
                from {opacity:0; transform:translateY(20px);}
                to {opacity:1; transform:translateY(0);}
            }

            .btn {
                display: inline-block;
                margin: 10px;
                padding: 14px 22px;
                border-radius: 10px;
                background: rgba(56,189,248,0.2);
                border: 1px solid #38bdf8;
                color: #38bdf8;
                text-decoration: none;
                transition: 0.3s;
            }

            .btn:hover {
                transform: translateY(-5px);
                box-shadow: 0 0 20px #38bdf8;
            }

            .card {
                display: inline-block;
                margin: 15px;
                padding: 20px;
                width: 250px;
                border-radius: 15px;
                background: rgba(255,255,255,0.05);
                backdrop-filter: blur(10px);
                transition: 0.4s;
            }

            .card:hover {
                transform: scale(1.05);
                box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            }
        </style>
    </head>

    <body>

        <h1>🚀 OpenEnv Ticket Routing AI</h1>
        <p>AI-powered customer support simulation environment</p>

        <div>
            <a class="btn" href="/docs">API Docs</a>
            <a class="btn" href="/tasks">Tasks</a>
            <a class="btn" href="/baseline">Baseline</a>
            <a class="btn" href="/health">Health</a>
        </div>

        <br><br>

        <div class="card">📌 Real-world Tasks</div>
        <div class="card">⚡ Smart Rewards</div>
        <div class="card">🤖 AI Ready</div>

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