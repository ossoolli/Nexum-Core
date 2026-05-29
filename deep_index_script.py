import os
import sqlite3
from nexum.memory.store import SovereignMemoryStore

def deep_index():
    store = SovereignMemoryStore(db_path="/home/madarmutaz/.hermes/state.db")
    project_dir = "/home/madarmutaz/Nexum-Core"
    indexed_count = 0
    lessons_learned = 0
    
    # 1. Index files
    for root, dirs, files in os.walk(project_dir):
        # Ignore some directories
        if any(ignored in root for ignored in ['.git', '__pycache__', '.pytest_cache', 'venv', 'logs']):
            continue
            
        for file in files:
            if file.endswith(('.py', '.md', '.json', '.yaml', '.go', '.proto')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(5000)
                        store.add_memory("SourceCodeIndex", f"Path: {file_path}\nContent: {content}")
                        indexed_count += 1
                except Exception as e:
                    print(f"Skipping {file_path}: {e}")

    # 2. Summarize logs as "Lessons Learned"
    log_files = ["storage/logs/err.log", "storage/logs/sentinel.log"]
    for log_path in log_files:
        full_path = os.path.join(project_dir, log_path)
        if os.path.exists(full_path):
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    recent_errors = "".join(lines[-20:]) # Get last 20 lines
                    store.add_memory("LessonsLearned", f"Log: {log_path}\nRecent Issues Summary: {recent_errors}")
                    lessons_learned += 1
            except Exception as e:
                print(f"Error reading log {log_path}: {e}")
                
    return indexed_count, lessons_learned

if __name__ == "__main__":
    count, lessons = deep_index()
    print(f"Indexed {count} documents and {lessons} lessons learned.")
