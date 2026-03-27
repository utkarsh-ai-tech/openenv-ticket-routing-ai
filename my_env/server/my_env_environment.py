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
    return """
    <html>
    <head>
        <title>OpenEnv Ticket Routing AI</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <style>
            body {
                margin: 0;
                font-family: 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #020617, #0f172a);
                color: white;
                overflow-x: hidden;
                overflow-y: auto;
            }

            /* 🌊 MULTI-LAYER WAVE */
            .wave, .wave2 {
                position: fixed;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(56,189,248,0.2), transparent 60%);
                animation: waveMove 12s linear infinite;
                z-index: 0;
            }

            .wave2 {
                animation-duration: 18s;
                opacity: 0.5;
            }

            .wave3 {
                position: fixed;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(56,189,248,0.15), transparent 60%);
                animation: waveMove 22s linear infinite;
                opacity: 0.3;
               z-index: 0;
            }

            @keyframes waveMove {
                0% { transform: translate(-25%, -25%) rotate(0deg); }
                50% { transform: translate(-20%, -30%) rotate(180deg); }
                100% { transform: translate(-25%, -25%) rotate(360deg); }
            }

            .container {
                position: relative;
                z-index: 1;
                text-align: center;
                padding: 80px 20px;
            }

            h1 {
                font-size: 50px;
                color: #38bdf8;
                text-shadow: 0 0 20px rgba(56,189,248,0.7);
            }

            p {
                color: #94a3b8;
                margin-bottom: 30px;
            }

            /* 🔘 BUTTONS */
            .buttons a {
                display: inline-block;
                margin: 10px;
                padding: 12px 22px;
                background: rgba(56,189,248,0.1);
                color: #38bdf8;
                border: 1px solid #38bdf8;
                border-radius: 10px;
                text-decoration: none;
                transition: 0.3s;
            }

            .buttons a:hover {
                background: #38bdf8;
                color: black;
                transform: translateY(-4px);
                box-shadow: 0 0 15px #38bdf8;
            }

            /* 🧊 CARDS */
            .cards {
                display: flex;
                justify-content: center;
                flex-wrap: wrap;
                gap: 20px;
                margin-top: 50px;
            }

            .card {
                width: 260px;
                padding: 20px;
                border-radius: 15px;
                background: rgba(255,255,255,0.05);
                backdrop-filter: blur(10px);
                box-shadow: 0 10px 30px rgba(0,0,0,0.4);
                transition: 0.4s;
            }

            .card:hover {
                transform: translateY(-10px) scale(1.05);
                box-shadow: 0 0 25px rgba(56,189,248,0.5);
            }

            .card h3 {
                color: #38bdf8;
            }

            /* ✨ FOOTER */
            .footer {
                margin-top: 60px;
                font-size: 14px;
                color: #94a3b8;
                opacity: 0.8;
            }
        </style>
    </head>

    <body>

        <!-- 🌊 BACKGROUND -->
        <div class="wave"></div>
        <div class="wave2"></div>
        <div class="wave3"></div>

        <div class="container">

            <h1>🚀 OpenEnv Ticket Routing AI</h1>
            <p>AI-powered customer support simulation with smart routing</p>

            <!-- 🔘 NAV BUTTONS WITH ICONS -->
            <div class="buttons">
                <a href="/docs">📄 API Docs</a>
                <a href="/tasks">📋 Tasks</a>
                <a href="/baseline">📊 Baseline</a>
                <a href="/health">💚 Health</a>
                <a href="/run-demo">⚡ Run Demo</a>
            </div>

            <!-- 🧊 CARDS -->
            <div class="cards">

                <div class="card">
                    <h3>⚙️ System Status</h3>
                    <p>Check API health and performance instantly.</p>
                </div>

                <div class="card">
                    <h3>📋 Smart Tasks</h3>
                    <p>Real-world support tickets with difficulty levels.</p>
                </div>

                <div class="card">
                    <h3>🤖 AI Engine</h3>
                    <p>Scoring, routing, and automated evaluation.</p>
                </div>

            </div>

            <!-- ✨ FOOTER -->
            <div class="footer">
                🚀 Built with passion by <b>Utkarsh</b>
            </div>

        </div>

    </body>
    </html>
    """

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