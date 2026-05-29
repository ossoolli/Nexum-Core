from core.memory.sovereign_memory import SovereignMemory

def verify_recall():
    mem = SovereignMemory(base_path="/home/madarmutaz/Nexum-Core/storage/sovereign_memory")
    
    queries = ["Nexum OS philosophy", "Security gateway design"]
    
    for query in queries:
        print(f"\nQuerying: '{query}'")
        results = mem.search_memory(query)
        print(f"Results: {results}")

if __name__ == "__main__":
    verify_recall()
