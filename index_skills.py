import os
from core.memory.sovereign_memory import SovereignMemory

def index_skills():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    mem = SovereignMemory(base_path=os.path.join(project_dir, "storage", "sovereign_memory"))
    skills_dirs = [
        os.path.join(project_dir, "storage", "skills"),
        os.path.join(project_dir, "optional-skills"),
        os.path.join(project_dir, "skills")
    ]
    
    files_to_index = []
    for skills_dir in skills_dirs:
        if os.path.exists(skills_dir):
            for root, dirs, files in os.walk(skills_dir):
                for file in files:
                    if file.endswith(".md"):
                        files_to_index.append(os.path.join(root, file))

    print(f"Found {len(files_to_index)} skills to index.")
    for file_path in files_to_index:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
                mem.add_memory(role=file_path, content=content)
                print(f"Indexed Skill: {file_path}")
        except Exception as e:
            print(f"Error indexing {file_path}: {e}")

if __name__ == "__main__":
    index_skills()
