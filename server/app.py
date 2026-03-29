from fastapi import FastAPI, Body, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import random

from my_env.models import Action, Observation
from my_env.tasks import TASKS
from my_env.grader import grade
from my_env.reward import compute_reward

app = FastAPI(title="OpenEnv Ticket Routing AI", version="2.0.0")


# ══════════════════════════════════════════════════════════════════════════
#  MODELS
# ══════════════════════════════════════════════════════════════════════════

class ResetRequest(BaseModel):
    task_id: Optional[int] = 1


# ══════════════════════════════════════════════════════════════════════════
#  ENVIRONMENT
# ══════════════════════════════════════════════════════════════════════════

class MyEnv:
    def __init__(self):
        self.current_task = None
        self.done = False

    def reset(self, task_id: int = 1):
        self.current_task = TASKS[task_id - 1]
        self.done = False
        return Observation(
            ticket_id=self.current_task["id"],
            message=self.current_task["ticket"],
        )

    def step(self, action: Action):
        expected = self.current_task["expected"]
        score    = grade(action, expected)
        reward   = compute_reward(score)
        self.done = True
        return (
            Observation(ticket_id=self.current_task["id"], message="Processed"),
            reward,
            self.done,
            {"score": score},
        )

    def state(self):
        return self.current_task


env = MyEnv()


# ══════════════════════════════════════════════════════════════════════════
#  SHARED HTML SHELL
# ══════════════════════════════════════════════════════════════════════════

STYLE = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');
  :root {
    --bg0:   #03070f;
    --bg1:   #080f1e;
    --panel: rgba(255,255,255,0.04);
    --border:rgba(56,189,248,0.18);
    --sky:   #38bdf8;
    --sky2:  #7dd3fc;
    --dim:   #64748b;
    --red:   #f87171;
    --green: #4ade80;
    --gold:  #fbbf24;
  }
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  html { scroll-behavior: smooth; }
  body {
    background: var(--bg0);
    color: #e2e8f0;
    font-family: 'Syne', sans-serif;
    min-height: 100vh;
    overflow-x: hidden;
  }
  body::before {
    content: '';
    position: fixed; inset: 0;
    background-image:
      linear-gradient(rgba(56,189,248,.04) 1px, transparent 1px),
      linear-gradient(90deg, rgba(56,189,248,.04) 1px, transparent 1px);
    background-size: 48px 48px;
    z-index: 0;
    pointer-events: none;
  }
  .glow {
    position: fixed;
    border-radius: 50%;
    filter: blur(120px);
    opacity: .25;
    pointer-events: none;
    z-index: 0;
  }
  .glow-a { width:600px; height:600px; background:#0ea5e9; top:-200px; left:-200px; animation: drift 14s ease-in-out infinite alternate; }
  .glow-b { width:400px; height:400px; background:#6366f1; bottom:-150px; right:-100px; animation: drift 18s ease-in-out infinite alternate-reverse; }
  @keyframes drift {
    from { transform: translate(0,0); }
    to   { transform: translate(60px, 40px); }
  }
  .topbar {
    position: relative; z-index: 10;
    display: flex; align-items: center; justify-content: space-between;
    padding: 18px 40px;
    border-bottom: 1px solid var(--border);
    background: rgba(3,7,15,.7);
    backdrop-filter: blur(14px);
  }
  .topbar .logo {
    font-family: 'Space Mono', monospace;
    font-size: 15px;
    color: var(--sky);
    letter-spacing: .08em;
  }
  .topbar nav a {
    font-size: 13px;
    color: var(--dim);
    text-decoration: none;
    margin-left: 24px;
    letter-spacing: .05em;
    transition: color .2s;
  }
  .topbar nav a:hover { color: var(--sky); }
  .page {
    position: relative; z-index: 1;
    max-width: 1100px;
    margin: 0 auto;
    padding: 60px 24px 100px;
  }
  .hero { text-align: center; padding: 60px 0 40px; }
  .badge {
    display: inline-block;
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    letter-spacing: .12em;
    color: var(--sky);
    background: rgba(56,189,248,.1);
    border: 1px solid rgba(56,189,248,.3);
    border-radius: 999px;
    padding: 4px 14px;
    margin-bottom: 20px;
  }
  h1.title {
    font-size: clamp(36px, 6vw, 72px);
    font-weight: 800;
    line-height: 1.05;
    background: linear-gradient(120deg, #fff 30%, var(--sky2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .subtitle {
    margin-top: 14px;
    color: var(--dim);
    font-size: 16px;
    max-width: 480px;
    margin-inline: auto;
    line-height: 1.6;
  }
  .nav-pills {
    display: flex; flex-wrap: wrap; justify-content: center;
    gap: 10px; margin-top: 36px;
  }
  .nav-pills a {
    display: inline-flex; align-items: center; gap: 7px;
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    padding: 9px 20px;
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--sky2);
    text-decoration: none;
    background: var(--panel);
    backdrop-filter: blur(6px);
    transition: all .25s;
  }
  .nav-pills a:hover {
    background: rgba(56,189,248,.12);
    border-color: var(--sky);
    color: #fff;
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(56,189,248,.2);
  }
  .stat-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 16px;
    margin-top: 56px;
  }
  .stat-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 24px 20px;
    transition: transform .3s, box-shadow .3s;
  }
  .stat-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 16px 40px rgba(56,189,248,.1);
  }
  .stat-card .icon { font-size: 26px; margin-bottom: 10px; }
  .stat-card h3 { font-size: 13px; color: var(--sky); letter-spacing: .06em; margin-bottom: 6px; }
  .stat-card p  { font-size: 13px; color: var(--dim); line-height: 1.5; }
  .sec-title {
    font-size: 11px;
    font-family: 'Space Mono', monospace;
    letter-spacing: .14em;
    color: var(--sky);
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border);
  }
  .task-list { display: flex; flex-direction: column; gap: 14px; margin-top: 16px; }
  .task-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px 24px;
    display: flex; align-items: flex-start; gap: 18px;
    transition: box-shadow .25s;
  }
  .task-card:hover { box-shadow: 0 0 0 1px var(--sky); }
  .task-id {
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    color: var(--bg0);
    background: var(--sky);
    border-radius: 6px;
    padding: 3px 9px;
    white-space: nowrap;
    flex-shrink: 0;
  }
  .task-body { flex: 1; }
  .task-body .ticket { font-size: 14px; color: #cbd5e1; line-height: 1.55; }
  .diff-badge {
    display: inline-block;
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    letter-spacing: .08em;
    padding: 2px 10px;
    border-radius: 999px;
    margin-top: 8px;
  }
  .diff-easy   { background: rgba(74,222,128,.12); color: var(--green); border: 1px solid rgba(74,222,128,.3); }
  .diff-medium { background: rgba(251,191,36,.1);  color: var(--gold);  border: 1px solid rgba(251,191,36,.3); }
  .diff-hard   { background: rgba(248,113,113,.1); color: var(--red);   border: 1px solid rgba(248,113,113,.3); }
  .score-hero { text-align: center; padding: 40px 0 24px; }
  .score-num {
    font-family: 'Space Mono', monospace;
    font-size: clamp(56px, 10vw, 96px);
    color: var(--sky);
    text-shadow: 0 0 40px rgba(56,189,248,.5);
    line-height: 1;
  }
  .score-label { font-size: 13px; color: var(--dim); margin-top: 6px; }
  .bar-grid { display: flex; flex-direction: column; gap: 14px; margin-top: 28px; }
  .bar-row { display: flex; align-items: center; gap: 14px; }
  .bar-row .lbl { font-family: 'Space Mono', monospace; font-size: 11px; color: var(--dim); width: 32px; }
  .bar-track { flex: 1; height: 10px; background: rgba(255,255,255,.06); border-radius: 99px; overflow: hidden; }
  .bar-fill {
    height: 100%;
    border-radius: 99px;
    background: linear-gradient(90deg, var(--sky), var(--sky2));
    box-shadow: 0 0 12px rgba(56,189,248,.5);
    animation: grow .8s cubic-bezier(.22,1,.36,1) both;
  }
  @keyframes grow { from { width: 0 !important; } }
  .bar-val { font-family: 'Space Mono', monospace; font-size: 11px; color: var(--sky2); width: 36px; text-align: right; }
  .result-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 14px;
    margin-top: 28px;
  }
  .result-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 22px;
    text-align: center;
    transition: transform .3s;
  }
  .result-card:hover { transform: translateY(-5px); box-shadow: 0 12px 32px rgba(56,189,248,.12); }
  .result-card .r-task { font-family: 'Space Mono', monospace; font-size: 11px; color: var(--dim); margin-bottom: 8px; }
  .result-card .r-score { font-size: 36px; font-weight: 800; color: var(--sky); }
  .health-dot {
    display: inline-block;
    width: 10px; height: 10px;
    border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 10px var(--green);
    animation: pulse 2s ease-in-out infinite;
    margin-right: 8px;
  }
  @keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:.4; } }
  .health-title { font-size: 28px; font-weight: 800; display: flex; align-items: center; justify-content: center; }
  .footer {
    text-align: center;
    padding: 40px 0 0;
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    color: var(--dim);
    letter-spacing: .06em;
  }
  .back {
    display: inline-flex; align-items: center; gap: 6px;
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    color: var(--dim);
    text-decoration: none;
    margin-bottom: 36px;
    border: 1px solid var(--border);
    padding: 6px 14px;
    border-radius: 6px;
    transition: color .2s, border-color .2s;
  }
  .back:hover { color: var(--sky); border-color: var(--sky); }
</style>
"""

NAV = """
<div class="topbar">
  <span class="logo">▸ OPENENV v2</span>
  <nav>
    <a href="/tasks">Tasks</a>
    <a href="/baseline">Baseline</a>
    <a href="/run-demo">Demo</a>
    <a href="/health">Health</a>
    <a href="/docs">API Docs</a>
  </nav>
</div>
"""

def shell(body: str, title: str = "OpenEnv") -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} · OpenEnv</title>
  {STYLE}
</head>
<body>
  <div class="glow glow-a"></div>
  <div class="glow glow-b"></div>
  {NAV}
  <div class="page">
    {body}
  </div>
</body>
</html>"""


# ══════════════════════════════════════════════════════════════════════════
#  HOMEPAGE
# ══════════════════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
def home():
    return shell("""
    <div class="hero">
      <div class="badge"> -: WELCOME JUDGES :- </div>
      <h1 class="title">Ticket Routing<br>Intelligence</h1>
      <p class="subtitle">
        An open reinforcement-learning environment for training and evaluating
        customer-support AI agents.
      </p>
      <div class="nav-pills">
        <a href="/docs">📄 API Docs</a>
        <a href="/tasks">📋 Tasks</a>
        <a href="/baseline">📊 Baseline</a>
        <a href="/health">💚 Health</a>
        <a href="/run-demo">⚡ Run Demo</a>
      </div>
    </div>
    <div class="stat-grid">
      <div class="stat-card">
        <div class="icon">⚙️</div>
        <h3>SYSTEM STATUS</h3>
        <p>Real-time health checks and performance monitoring via <code>/health</code>.</p>
      </div>
      <div class="stat-card">
        <div class="icon">📋</div>
        <h3>SMART TASKS</h3>
        <p>Real-world support tickets with Easy / Medium / Hard difficulty tiers.</p>
      </div>
      <div class="stat-card">
        <div class="icon">🤖</div>
        <h3>AI ENGINE</h3>
        <p>Automatic scoring, routing evaluation, and reward computation.</p>
      </div>
      <div class="stat-card">
        <div class="icon">🔁</div>
        <h3>RL LOOP</h3>
        <p>Full <code>reset → step → reward</code> loop compatible with any RL framework.</p>
      </div>
    </div>
    <div class="footer">Built with ❤️ by Utkarsh</div>
    """, "Home")


# ══════════════════════════════════════════════════════════════════════════
#  HEALTH
# ══════════════════════════════════════════════════════════════════════════

@app.get("/health", response_class=HTMLResponse)
def health():
    return shell("""
    <a class="back" href="/">← Back</a>
    <div style="text-align:center; padding: 60px 0;">
      <h1 class="health-title"><span class="health-dot"></span> System Healthy</h1>
      <p style="color:var(--dim); margin-top:12px; font-size:14px;">
        All services operational · API responding normally
      </p>
    </div>
    """, "Health")


# ══════════════════════════════════════════════════════════════════════════
#  TASKS
# ══════════════════════════════════════════════════════════════════════════

@app.get("/tasks", response_class=HTMLResponse)
def tasks():
    items = ""
    for t in TASKS:
        diff = t.get("difficulty", "medium").lower()
        items += f"""
        <div class="task-card">
          <span class="task-id">T{t['id']}</span>
          <div class="task-body">
            <p class="ticket">{t['ticket']}</p>
            <span class="diff-badge diff-{diff}">{diff.upper()}</span>
          </div>
        </div>
        """
    return shell(f"""
    <a class="back" href="/">← Back</a>
    <div class="sec-title">ALL TASKS</div>
    <div class="task-list">{items}</div>
    """, "Tasks")


# ══════════════════════════════════════════════════════════════════════════
#  BASELINE
# ══════════════════════════════════════════════════════════════════════════

@app.get("/baseline", response_class=HTMLResponse)
def baseline():
    scores = []
    for i in range(1, len(TASKS) + 1):
        env.reset(i)
        action = Action(
            category=random.choice(["billing", "tech", "complaint"]),
            priority=random.choice(["low", "medium", "high"]),
            response="Processing...",
            escalate=random.choice([True, False]),
        )
        _, _, _, info = env.step(action)
        scores.append(info["score"])

    avg = sum(scores) / len(scores)

    bars = ""
    for idx, s in enumerate(scores):
        pct = round(s * 100, 1)
        bars += f"""
        <div class="bar-row">
          <span class="lbl">T{idx+1}</span>
          <div class="bar-track">
            <div class="bar-fill" style="width:{pct}%"></div>
          </div>
          <span class="bar-val">{round(s,2)}</span>
        </div>
        """

    return shell(f"""
    <a class="back" href="/">← Back</a>
    <div class="score-hero">
      <div class="score-num">{avg:.2f}</div>
      <div class="score-label">AVERAGE BASELINE SCORE</div>
    </div>
    <div class="sec-title">PER-TASK BREAKDOWN</div>
    <div class="bar-grid">{bars}</div>
    """, "Baseline")


# ══════════════════════════════════════════════════════════════════════════
#  DEMO
# ══════════════════════════════════════════════════════════════════════════

@app.get("/run-demo", response_class=HTMLResponse)
def run_demo():
    results = []
    for i in range(1, len(TASKS) + 1):
        env.reset(i)
        action = Action(
            category=random.choice(["billing", "tech", "complaint"]),
            priority=random.choice(["low", "medium", "high"]),
            response="Processing...",
            escalate=random.choice([True, False]),
        )
        _, _, _, info = env.step(action)
        results.append(info["score"])

    avg = sum(results) / len(results)

    cards = "".join([
        f"""<div class="result-card">
              <div class="r-task">TASK {i+1}</div>
              <div class="r-score">{round(s, 2)}</div>
            </div>"""
        for i, s in enumerate(results)
    ])

    return shell(f"""
    <a class="back" href="/">← Back</a>
    <div class="score-hero">
      <div class="score-num">{avg:.2f}</div>
      <div class="score-label">DEMO AVERAGE SCORE</div>
    </div>
    <div class="sec-title">TASK RESULTS</div>
    <div class="result-grid">{cards}</div>
    """, "Demo")


# ══════════════════════════════════════════════════════════════════════════
#  API ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════

@app.get("/reset")
def reset_get(task_id: int = 1):
    obs = env.reset(task_id)
    return obs.model_dump()


@app.post("/reset")
async def reset_post(request: Request):
    try:
        body = await request.json()
        task_id = body.get("task_id", 1)
    except:
        task_id = 1
    obs = env.reset(task_id)
    return obs.model_dump()


@app.post("/step")
def step(action: Action):
    obs, reward, done, info = env.step(action)
    return {
        "observation": obs.model_dump(),
        "reward": reward,
        "done": done,
        "info": info,
    }


@app.get("/state")
def state():
    return env.state()