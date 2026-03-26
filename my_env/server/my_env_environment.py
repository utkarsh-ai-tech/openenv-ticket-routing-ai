from fastapi import FastAPI
from fastapi.responses import HTMLResponse
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
                background: linear-gradient(135deg, #020617, #0f172a);
                color: white;
                overflow-x: hidden;
            }

            /* 🌊 WAVE BACKGROUND */
            .wave {
                position: absolute;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle at 50% 50%, rgba(56,189,248,0.15), transparent);
                animation: waveMove 8s linear infinite;
            }

            @keyframes waveMove {
                0% { transform: translate(-25%, -25%); }
                50% { transform: translate(-20%, -30%); }
                100% { transform: translate(-25%, -25%); }
            }

            .container {
                position: relative;
                text-align: center;
                padding: 80px 20px;
            }

            h1 {
                font-size: 50px;
                color: #38bdf8;
            }

            p {
                color: #94a3b8;
            }

            .buttons a {
                margin: 10px;
                padding: 12px 20px;
                background: #38bdf8;
                color: black;
                border-radius: 8px;
                text-decoration: none;
                transition: 0.3s;
            }

            .buttons a:hover {
                background: #0ea5e9;
                transform: translateY(-3px);
            }

            /* 🧊 CARDS */
            .cards {
                display: flex;
                justify-content: center;
                flex-wrap: wrap;
                margin-top: 50px;
                gap: 20px;
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
                transform: translateY(-10px);
            }

            .card h3 {
                color: #38bdf8;
            }
        </style>
    </head>

    <body>

        <div class="wave"></div>

        <div class="container">
            <h1>🚀 OpenEnv Ticket Routing AI</h1>
            <p>AI-powered customer support simulation</p>

            <div class="buttons">
                <a href="/docs">API Docs</a>
                <a href="/tasks">Tasks</a>
                <a href="/baseline">Baseline</a>
                <a href="/health">Health</a>
                <a href="/run-demo">Run Demo</a>
            </div>

            <div class="cards">

                <div class="card">
                    <h3>⚙️ System Status</h3>
                    <p>Check API health, baseline score and system performance.</p>
                </div>

                <div class="card">
                    <h3>📋 Tasks</h3>
                    <p>Explore real-world customer support tickets with difficulty levels.</p>
                </div>

                <div class="card">
                    <h3>🤖 AI Features</h3>
                    <p>Supports RL agents, scoring system and automated evaluation.</p>
                </div>

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

@app.get("/baseline", response_class=HTMLResponse)
def baseline():
    import random

    scores = []

    categories = ["billing", "tech", "complaint"]
    priorities = ["low", "medium", "high"]

    for i in range(1, 4):
        env.reset(i)

        action = Action(
            category=random.choice(categories),
            priority=random.choice(priorities),
            response="We are checking your issue, please wait.",
            escalate=random.choice([True, False])
        )

        _, _, _, info = env.step(action)
        scores.append(info["score"])

    avg = sum(scores) / len(scores)

    # 🎯 GRAPH VALUES
    graph_data = ",".join(str(round(s,2)) for s in scores)

    return f"""
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>

    <body style="background:#020617;color:white;text-align:center;padding:50px;font-family:sans-serif;">

        <h1 style="color:#38bdf8;">📊 Baseline Performance</h1>
        <h2>Average Score: {avg:.2f}</h2>

        <canvas id="myChart" width="400" height="200"></canvas>

        <script>
            const ctx = document.getElementById('myChart');

            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: ["Task 1", "Task 2", "Task 3"],
                    datasets: [{{
                        label: 'Score',
                        data: [{graph_data}],
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            max: 1
                        }}
                    }}
                }}
            }});
        </script>

        <br><br>
        <a href="/" style="color:#38bdf8;">⬅ Back to Home</a>

    </body>
    </html>
    """
@app.get("/tasks", response_class=HTMLResponse)
def get_tasks():
    html = """
    <html>
    <body style="background:#020617;color:white;font-family:sans-serif;padding:40px;">
    <h1 style="text-align:center;color:#38bdf8;">📋 Tasks</h1>
    <div style="display:flex;flex-wrap:wrap;justify-content:center;">
    """

    for t in TASKS:
        html += f"""
        <div style="background:rgba(255,255,255,0.05);padding:20px;margin:15px;border-radius:10px;width:250px;">
            <h3>Task {t['id']}</h3>
            <p><b>Difficulty:</b> {t['difficulty']}</p>
            <p>{t['ticket']}</p>
        </div>
        """

    html += """
    </div>
    <div style="text-align:center;margin-top:20px;">
        <a href="/" style="color:#38bdf8;">⬅ Back</a>
    </div>
    </body>
    </html>
    """

    return html

@app.get("/grader")
def get_grader():
    if env.current_task is None:
        return {"error": "No task running"}

    return {
        "task_id": env.current_task["id"],
        "expected": env.current_task["expected"]
    }

@app.get("/health", response_class=HTMLResponse)
def health():
    return """
    <html>
    <body style="background:#020617;color:white;text-align:center;padding:80px;font-family:sans-serif;">
        <h1 style="color:#38bdf8;">✅ System Healthy</h1>
        <p>All services are running perfectly 🚀</p>
        <a href="/" style="color:#38bdf8;">⬅ Back to Home</a>
    </body>
    </html>
    """

@app.get("/run-demo")
def run_demo():
    results = []

    for i in range(1, 4):
        env.reset(i)

        action = Action(
            category="billing",
            priority="medium",
            response="We are checking your issue.",
            escalate=False
        )

        _, _, _, info = env.step(action)

        results.append({
            "task_id": i,
            "score": info["score"]
        })

    return {"demo_results": results}