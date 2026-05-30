# Memory Indexing Optimization & Log Processing

In sovereign agentic operating systems like `Nexum-Core`, indexing the codebase and operational logs into full-text search (FTS5) databases is critical for self-healing and context recall. However, naive indexing scripts often suffer from fatal performance bottlenecks.

## 1. The Walk-Hanging Problem (os.walk)
When traversing a repository codebase with `os.walk`, the traversal is recursive. In Python, `os.walk` will descend into every directory unless explicitly instructed otherwise. If the directory contains large structures like:
- **`venv/` or `.venv/`:** (Virtual environments containing tens of thousands of library files).
- **`.git/`:** (Git objects database).
- **`__pycache__` & `.pytest_cache`:** (Compiled bytecode and test metadata).
- **Nested clone repositories:** (e.g., a secondary cloned repository within the directory).

This causes the indexer to hang, consume excessive RAM, or trigger execution timeouts (typically 60s or more).

### The Solution: In-Place Directory Pruning
To prevent `os.walk` from descending into ignored directories, modify the `dirs` list *in-place* inside the loop. `os.walk` reads the `dirs` list at each step, and modifying it (using slice assignment `dirs[:]`) controls which subdirectories are visited next:

```python
ignore_dirs = {'venv', '.git', '__pycache__', '.pytest_cache', '.claude', 'Nexum-Core', 'home', 'storage', 'skills'}

for root, dirs, files in os.walk(project_dir):
    # Modify dirs in-place to prune the traversal tree immediately
    dirs[:] = [d for d in dirs if d not in ignore_dirs]
    
    for file in files:
        # Index files safely...
```

---

## 2. High-Performance Log Processing
Logs can grow to hundreds of megabytes. Reading entire log files into memory is slow and risks system crashes. Since the most valuable errors and operational telemetry are recorded recently, the indexer should read the **tail** of the logs.

### Recommended Pattern: seek-from-end
Open the file in binary mode or seek to the end, then read the last N bytes (e.g., 8KB) to retrieve the latest warnings and traceback errors:

```python
try:
    with open(log_path, 'r', encoding='utf-8') as f:
        # Seek to the end of the file
        f.seek(0, os.SEEK_END)
        size = f.tell()
        
        # Read the last 8KB of data
        read_size = min(size, 8000)
        f.seek(max(0, size - read_size))
        content = f.read(read_size)
        
        if content.strip():
            memory.add_memory(f"Log_Index_{file}", f"SContext:\n{content}")
except Exception as e:
    print(f"Error indexing log: {e}")
```

---

## 3. Running & Execution Path
Always execute the indexing scripts from the project root with the correct `PYTHONPATH` so that local import modules (like `core` or `nexum`) can resolve cleanly:

```bash
# Execute from /home/madarmutaz/Nexum-Core
PYTHONPATH=. python3 nexum/memory/indexer.py
```
