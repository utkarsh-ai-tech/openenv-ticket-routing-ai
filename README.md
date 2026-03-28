
---
title: OpenEnv Ticket Routing AI
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# 🚀 Ticket Routing Environment (OpenEnv)

## 📌 1. Overview

This project implements a **real-world AI environment** where an agent performs **customer support ticket triaging and resolution**.

The agent must:

* Understand user complaints
* Classify tickets into categories
* Assign priority levels
* Generate a response
* Decide whether escalation is required

This environment follows the **OpenEnv specification** and is designed for **training and evaluating intelligent agents (LLMs/RL agents)**.

---

## 🎯 2. Motivation

Customer support automation is a **real-world high-impact problem**.
This environment simulates realistic workflows used in:

* SaaS companies
* E-commerce platforms
* Tech support systems

It helps evaluate how well an AI agent can make **multi-step decisions** under constraints.

---

## 🧠 3. Environment Design

### 🔹 Action Space

| Field    | Type | Description                |
| -------- | ---- | -------------------------- |
| category | str  | billing / tech / complaint |
| priority | str  | low / medium / high        |
| response | str  | text reply to the user     |
| escalate | bool | whether to escalate issue  |

---

### 🔹 Observation Space

| Field     | Type | Description           |
| --------- | ---- | --------------------- |
| ticket_id | int  | unique identifier     |
| message   | str  | customer complaint    |
| history   | str  | optional conversation |

---

### 🔹 Reward Function

* Range: **0.0 → 1.0**
* Partial rewards for:

  * Correct category
  * Correct priority
  * Correct escalation decision
  * Meaningful response
* Penalizes incorrect or poor actions

---

## 🧪 4. Tasks (Difficulty Progression)

| Task | Difficulty | Description                               |
| ---- | ---------- | ----------------------------------------- |
| 1    | Easy       | Billing issue (double charge)             |
| 2    | Medium     | Technical issue (app crash)               |
| 3    | Hard       | Emotional complaint with repeated failure |

✔ Tasks increase in complexity and require better reasoning.

---

## ⚙️ 5. API Endpoints

| Endpoint    | Method | Description          |
| ----------- | ------ | -------------------- |
| `/reset`    | GET    | Start a new task     |
| `/step`     | POST   | Take an action       |
| `/state`    | GET    | Get current state    |
| `/baseline` | GET    | Run baseline agent   |
| `/tasks`    | GET    | List all tasks       |
| `/grader`   | GET    | Show expected output |
| `/health`   | GET    | Server status check  |

---

## 🖥️ 6. How to Run (Local Setup)

### Step 1: Clone Repository

```bash
git clone <your-repo-link>
cd ticket-routing-env
```

### Step 2: Install Dependencies

```bash
pip install fastapi uvicorn pydantic requests
```

### Step 3: Start Server

```bash
uvicorn my_env.server.my_env_environment:app --reload
```

### Step 4: Open in Browser

```
http://127.0.0.1:8000/docs
```

👉 Use Swagger UI to test endpoints interactively.

---

