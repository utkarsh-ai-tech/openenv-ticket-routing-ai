TASKS = [
    {
        "id": 1,
        "difficulty": "easy",
        "ticket": "I was charged twice for my order",
        "expected": {
            "category": "billing",
            "priority": "medium",
            "escalate": False
        }
    },
    {
        "id": 2,
        "difficulty": "medium",
        "ticket": "My app crashes when I open it",
        "expected": {
            "category": "tech",
            "priority": "high",
            "escalate": True
        }
    },
     {
       "id": 3,
       "difficulty": "hard",
       "ticket": "I have been charged twice, my app crashes, and this is the third time this happened. I am very frustrated!",
       "expected": {
           "category": "complaint",
          "priority": "high",
          "escalate": True
        }
    }
]