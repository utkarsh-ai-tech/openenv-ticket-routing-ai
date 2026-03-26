from my_env.server.my_env_environment import MyEnv
from my_env.models import Action

def smart_agent(message):
    message = message.lower()

    if "charged" in message or "payment" in message:
        return Action(category="billing", priority="medium", response="We are checking your billing issue", escalate=False)

    elif "crash" in message or "error" in message:
        return Action(category="tech", priority="high", response="We are investigating the technical issue", escalate=True)

    elif "unhappy" in message or "failed" in message:
        return Action(category="complaint", priority="high", response="We are sorry for the inconvenience", escalate=True)

    return Action(category="complaint", priority="low", response="We will look into it", escalate=False)


env = MyEnv()
scores = []

for i in range(1, 4):
    obs = env.reset(i)
    action = smart_agent(obs.message)
    _, _, _, info = env.step(action)
    scores.append(info["score"])

print("Smart Baseline Score:", sum(scores)/len(scores))