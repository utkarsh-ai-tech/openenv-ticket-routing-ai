def grade(action, expected):
    score = 0.0

    if action.category == expected["category"]:
        score += 0.4

    if action.priority == expected["priority"]:
        score += 0.3

    if action.escalate == expected["escalate"]:
        score += 0.2

    if len(action.response) > 10:
        score += 0.1

    return min(score, 1.0)