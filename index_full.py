import os
import sys
from core.memory.sovereign_memory import SovereignMemory

def index_data():
    mem = SovereignMemory(base_path="/home/madarmutaz/Nexum-Core/storage/sovereign_memory")
    project_dir = "/home/madarmutaz/Nexum-Core"
    logs_dir = os.path.join(project_dir, "storage/logs")
    docs_dir = os.path.join(project_dir, "docs")
    protocols_dir = os.path.join(project_dir, "storage/protocols")
    readme_path = os.path.join(project_dir, "README.md")

    files_to_index = []

    # 1. Add Logs
    if os.path.exists(logs_dir):
        for root, dirs, files in os.walk(logs_dir):
            for file in files:
                if file.endswith(".log"):
                    files_to_index.append(os.path.join(root, file))

    # 2. Add Docs
    if os.path.exists(docs_dir):
        for root, dirs, files in os.walk(docs_dir):
            for file in files:
                if file.endswith((".md", ".txt")):
                    files_to_index.append(os.path.join(root, file))

    # 3. Add Protocols
    if os.path.exists(protocols_dir):
        for root, dirs, files in os.walk(protocols_dir):
            for file in files:
                if file.endswith((".yaml", ".yml", ".json")):
                    files_to_index.append(os.path.join(root, file))

    if os.path.exists(readme_path):
        files_to_index.append(readme_path)

    # Indexing
    print(f"Found {len(files_to_index)} files to index.")
    for file_path in files_to_index:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
                mem.add_memory(role=file_path, content=content)
                print(f"Indexed: {file_path}")
        except Exception as e:
            print(f"Error indexing {file_path}: {e}")

if __name__ == "__main__":
    index_data()
