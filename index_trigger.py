import os
import subprocess
import time

import sys

def check_and_index():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    # List of directories to check for new files
    check_dirs = [
        os.path.join(project_dir, "storage", "logs"),
        os.path.join(project_dir, "docs")
    ]
    
    # Store last check time
    last_check_file = os.path.join(project_dir, "last_index_time.txt")
    if os.path.exists(last_check_file):
        with open(last_check_file, 'r') as f:
            last_check_time = float(f.read())
    else:
        last_check_time = 0

    new_files_found = False
    for directory in check_dirs:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.exists(file_path):
                    if os.path.getmtime(file_path) > last_check_time:
                        new_files_found = True
                        break
        if new_files_found:
            break
            
    if new_files_found:
        print("New logs or docs detected, running re-index...")
        script_path = os.path.join(project_dir, "index_all_logs_and_docs.py")
        subprocess.run([sys.executable, script_path], env={"PYTHONPATH": project_dir})
        with open(last_check_file, 'w') as f:
            f.write(str(time.time()))
    else:
        print("No new changes detected.")

if __name__ == "__main__":
    check_and_index()
