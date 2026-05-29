from types import SimpleNamespace
from nexum.intelligence.orchestrator import Orchestrator

# Mock config
config = SimpleNamespace(
    thinker_model="anthropic/claude-3-opus",
    executor_model="gpt-4o-mini"
)

orchestrator = Orchestrator(config)

def test_routing():
    tasks = [
        ("Design a new system architecture", "anthropic/claude-3-opus"),
        ("Run a python script to delete files", "gpt-4o-mini"),
        ("Research the best way to implement a new feature", "anthropic/claude-3-opus"),
        ("Echo 'hello'", "gpt-4o-mini")
    ]
    
    for task, expected_model in tasks:
        model = orchestrator.route_task(task)
        assert model == expected_model, f"Expected {expected_model}, got {model} for task: {task}"
        print(f"Task: '{task}' -> Routed to {model}")

if __name__ == "__main__":
    test_routing()
    print("Orchestrator verification successful!")
