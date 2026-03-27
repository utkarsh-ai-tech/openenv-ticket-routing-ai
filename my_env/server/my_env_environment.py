from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from my_env.models import Action, Observation
from my_env.tasks import TASKS
from my_env.grader import grade
from my_env.reward import compute_reward
import random

app = FastAPI()

# ================= ENV =================
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

# ================= COMMON STYLE =================
def base_html(content):
    return f"""
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{
                margin:0;
                font-family: 'Segoe UI', sans-serif;
                background: linear-gradient(135deg,#020617,#0f172a);
                color:white;
            }}

            .wave {{
                position: fixed;
                width:200%;
                height:200%;
                background: radial-gradient(circle, rgba(56,189,248,0.2), transparent 60%);
                animation: wave 10s linear infinite;
                z-index:0;
            }}

            @keyframes wave {{
                0% {{ transform: translate(-25%,-25%) rotate(0); }}
                50% {{ transform: translate(-20%,-30%) rotate(180deg); }}
                100% {{ transform: translate(-25%,-25%) rotate(360deg); }}
            }}

            .container {{
                position:relative;
                z-index:1;
                text-align:center;
                padding:60px;
            }}

            .card {{
                background: rgba(255,255,255,0.05);
                padding:20px;
                margin:10px;
                border-radius:12px;
                display:inline-block;
                transition:0.3s;
            }}

            .card:hover {{
                transform:translateY(-8px);
            }}

            a {{
                color:#38bdf8;
                text-decoration:none;
            }}
        </style>
    </head>
    <body>
        <div class="wave"></div>
        <div class="container">
            {content}
            <br><br><a href="/">⬅ Back Home</a>
        </div>
    </body>
    </html>
    """

# ================= HOMEPAGE =================
@app.get("/", response_class=HTMLResponse)
def home():
    return base_html("""
        <h1>🚀 OpenEnv Ticket Routing AI</h1>
        <p>AI-powered customer support simulation</p>

        <div>
            <a href="/docs">Docs</a> |
            <a href="/tasks">Tasks</a> |
            <a href="/baseline">Baseline</a> |
            <a href="/health">Health</a> |
            <a href="/run-demo">Run Demo</a>
        </div>

        <br>

        <div class="card"><h3>⚙️ System</h3><p>Health + API</p></div>
        <div class="card"><h3>📋 Tasks</h3><p>3 difficulty levels</p></div>
        <div class="card"><h3>🤖 AI</h3><p>Scoring system</p></div>
    """)

# ================= HEALTH =================
@app.get("/health", response_class=HTMLResponse)
def health():
    return base_html("""
        <h1>✅ System Healthy</h1>
        <p>All services are running smoothly</p>
    """)

# ================= TASKS =================
@app.get("/tasks", response_class=HTMLResponse)
def tasks():
    cards = ""
    for t in TASKS:
        cards += f"""
        <div class="card">
            <h3>Task {t['id']}</h3>
            <p>{t['ticket']}</p>
            <p><b>{t['difficulty']}</b></p>
        </div>
        """
    return base_html(f"<h1>📋 Tasks</h1>{cards}")

# ================= BASELINE =================
@app.get("/baseline", response_class=HTMLResponse)
def baseline():
    scores = []

    for i in range(1, 4):
        env.reset(i)
        action = Action(
            category=random.choice(["billing","tech","complaint"]),
            priority=random.choice(["low","medium","high"]),
            response="Processing...",
            escalate=random.choice([True, False])
        )
        _, _, _, info = env.step(action)
        scores.append(info["score"])

    avg = sum(scores)/len(scores)
    graph = ",".join(str(round(s,2)) for s in scores)

    return base_html(f"""
        <h1>📊 Baseline Score</h1>
        <h2>{avg:.2f}</h2>
        <canvas id="chart"></canvas>

        <script>
        new Chart(document.getElementById('chart'), {{
            type:'bar',
            data:{{labels:["T1","T2","T3"],datasets:[{{data:[{graph}]}}]}}
        }});
        </script>
    """)

# ================= DEMO =================
@app.get("/run-demo", response_class=HTMLResponse)
def run_demo():
    results = []

    for i in range(1, 4):
        env.reset(i)
        action = Action(
            category=random.choice(["billing","tech","complaint"]),
            priority=random.choice(["low","medium","high"]),
            response="Processing...",
            escalate=random.choice([True, False])
        )
        _, _, _, info = env.step(action)
        results.append(info["score"])

    avg = sum(results)/len(results)

    cards = "".join([f"<div class='card'>Task {i+1}<br>{round(s,2)}</div>" for i,s in enumerate(results)])

    return base_html(f"""
        <h1>🚀 Demo Results</h1>
        <h2>{avg:.2f}</h2>
        {cards}
    """)

# ================= API =================
@app.get("/reset")
def reset(task_id: int = 1):
    return env.reset(task_id).model_dump()

@app.post("/step")
def step(action: Action):
    obs, reward, done, info = env.step(action)
    return {"observation": obs.model_dump(), "reward": reward, "done": done, "info": info}

@app.get("/state")
def state():
    return env.state()