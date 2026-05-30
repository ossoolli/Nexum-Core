import os
import sys
from core.memory.sovereign_memory import SovereignMemory

def index_files():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    mem = SovereignMemory(base_path=os.path.join(project_dir, "storage", "sovereign_memory"))
    
    files_to_index = [
        "README.md",
        "docs/ARCHITECTURE.md",
        "docs/CONTEXT.md",
    ]
    
    # Walk through key directories
    target_dirs = ["core", "nexum", "handlers", "services", "swarm", "scripts", "plugins", "tools", "optional-skills", "optional-mcps", "skills"]
    
    for dir_name in target_dirs:
        dir_path = os.path.join(project_dir, dir_name)
        if os.path.exists(dir_path):
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    if file.endswith((".py", ".md", ".go", ".yaml", ".json")):
                        files_to_index.append(os.path.join(root, file))

    log_file = os.path.join(project_dir, "storage", "logs", "evolution.log")
    
    with open(log_file, "a") as f:
        for file_path in files_to_index:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
                    mem.add_memory(role=file_path, content=content[:2000]) # Truncate for efficiency
                    f.write(f"Indexed: {file_path}\n")
                    print(f"Indexed: {file_path}")
            except Exception as e:
                print(f"Error indexing {file_path}: {e}")
                f.write(f"Error indexing {file_path}: {e}\n")

if __name__ == "__main__":
    index_files()
