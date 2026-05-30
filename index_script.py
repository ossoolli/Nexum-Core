import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from core.memory.sovereign_memory import SovereignMemory

# Initialize
mem = SovereignMemory(base_path=os.path.join(BASE_DIR, "storage", "sovereign_memory"))

# 1. Logs
log_dir = os.path.join(BASE_DIR, "storage", "logs")
count = 0
for root, dirs, files in os.walk(log_dir):
    for file in files:
        if file.endswith(".log"):
            path = os.path.join(root, file)
            with open(path, 'r', errors='ignore') as f:
                content = f.read()
                if content:
                    mem.add_memory("log", f"Log from {path}: {content[:500]}")
                    count += 1

# 2. Docs
docs_dir = os.path.join(BASE_DIR, "docs")
for root, dirs, files in os.walk(docs_dir):
    for file in files:
        if file.endswith(".md"):
            path = os.path.join(root, file)
            with open(path, 'r', errors='ignore') as f:
                content = f.read()
                mem.add_memory("docs", f"Doc from {path}: {content[:500]}")
                count += 1

# 3. README
readme = os.path.join(BASE_DIR, "README.md")
if os.path.exists(readme):
    with open(readme, 'r', errors='ignore') as f:
        content = f.read()
        mem.add_memory("docs", f"README: {content[:500]}")
        count += 1

print(f"Successfully indexed {count} items.")
