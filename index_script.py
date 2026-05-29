import sys
import os

# Add Nexum-Core to path if needed
sys.path.append("/home/madarmutaz/Nexum-Core")

from core.memory.sovereign_memory import SovereignMemory

# Initialize
mem = SovereignMemory(base_path="/home/madarmutaz/Nexum-Core/storage/sovereign_memory")

# 1. Logs
log_dir = "/home/madarmutaz/Nexum-Core/storage/logs"
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
docs_dir = "/home/madarmutaz/Nexum-Core/docs"
for root, dirs, files in os.walk(docs_dir):
    for file in files:
        if file.endswith(".md"):
            path = os.path.join(root, file)
            with open(path, 'r', errors='ignore') as f:
                content = f.read()
                mem.add_memory("docs", f"Doc from {path}: {content[:500]}")
                count += 1

# 3. README
readme = "/home/madarmutaz/Nexum-Core/README.md"
if os.path.exists(readme):
    with open(readme, 'r', errors='ignore') as f:
        content = f.read()
        mem.add_memory("docs", f"README: {content[:500]}")
        count += 1

print(f"Successfully indexed {count} items.")
