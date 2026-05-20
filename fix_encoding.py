import os

file_path = "main.py"
try:
    with open(file_path, "r", encoding="utf-16") as f:
        content = f.read()
except UnicodeError:
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except Exception as e:
        content = None

if content:
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Done converting main.py to UTF-8")
else:
    print("Failed to read main.py")
