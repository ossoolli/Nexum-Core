from core.memory.sovereign_memory import SovereignMemory

def verify_recall():
    mem = SovereignMemory(base_path="/home/madarmutaz/Nexum-Core/storage/sovereign_memory")
    
    queries = ["Security Architecture", "Architecture", "Nexum"]
    
    for query in queries:
        print(f"\nQuerying: '{query}'")
        results = mem.search_memory(query)
        print(f"Results: {len(results)} matches found")
        for res in results[:2]: # Just show first 2
            print(f"Role: {res['role']}, Timestamp: {res['timestamp']}")

if __name__ == "__main__":
    verify_recall()
