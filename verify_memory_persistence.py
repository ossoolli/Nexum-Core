import os
import sqlite3
from core.memory.sovereign_memory import SovereignMemory

def test_memory_persistence():
    # Define db path
    db_path = "/home/madarmutaz/.hermes/state.db"
    
    # 1. Initialize SovereignMemory
    mem = SovereignMemory(base_path="/home/madarmutaz/Nexum-Core/storage/sovereign_memory")
    
    # 2. Write a dummy memory
    test_content = "System Memory: This is a persistent test entry."
    mem.add_memory("system", test_content)
    print("Memory added.")
    
    # 3. Retrieve it
    results = mem.search_memory("System Memory")
    print(f"Search results: {results}")
    
    found = False
    for res in results:
        if test_content in res['content']:
            found = True
            break
            
    if found:
        print("Success: Memory entry found.")
    else:
        print("Error: Memory entry not found.")

if __name__ == "__main__":
    test_memory_persistence()
