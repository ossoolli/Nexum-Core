from core.memory.sovereign_memory import SovereignMemory

def verify_recall():
    import os
    project_dir = os.path.dirname(os.path.abspath(__file__))
    mem = SovereignMemory(base_path=os.path.join(project_dir, "storage", "sovereign_memory"))
    
    query = "example_dag"
    
    print(f"\nQuerying: '{query}'")
    results = mem.search_memory(query)
    print(f"Results: {results}")

if __name__ == "__main__":
    verify_recall()
