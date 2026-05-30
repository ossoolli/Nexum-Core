from core.memory.sovereign_memory import SovereignMemory

def verify_recall():
    import os
    project_dir = os.path.dirname(os.path.abspath(__file__))
    mem = SovereignMemory(base_path=os.path.join(project_dir, "storage", "sovereign_memory"))
    
    queries = ["Security Architecture", "Architecture", "Nexum"]
    
    for query in queries:
        print(f"\nQuerying: '{query}'")
        results = mem.search_memory(query)
        print(f"Results: {len(results)} matches found")
        for res in results[:2]: # Just show first 2
            print(f"Role: {res['role']}, Timestamp: {res['timestamp']}")

if __name__ == "__main__":
    verify_recall()
