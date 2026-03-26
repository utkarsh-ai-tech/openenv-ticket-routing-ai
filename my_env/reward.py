def compute_reward(score, action=None):
    reward = score

    # bonus for escalation in hard cases
    if action and action.escalate:
        reward += 0.05

    # penalty for too short response
    if action and len(action.response) < 5:
        reward -= 0.2

    return max(min(reward, 1.0), -1.0)