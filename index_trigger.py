import os
import subprocess
import time

def check_and_index():
    # List of directories to check for new files
    check_dirs = [
        "/home/madarmutaz/Nexum-Core/storage/logs",
        "/home/madarmutaz/Nexum-Core/docs"
    ]
    
    # Store last check time
    last_check_file = "/home/madarmutaz/Nexum-Core/last_index_time.txt"
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
                if os.path.getmtime(file_path) > last_check_time:
                    new_files_found = True
                    break
        if new_files_found:
            break
            
    if new_files_found:
        print("New logs or docs detected, running re-index...")
        subprocess.run(["python3", "/home/madarmutaz/Nexum-Core/index_all_logs_and_docs.py"], env={"PYTHONPATH": "/home/madarmutaz/Nexum-Core/"})
        with open(last_check_file, 'w') as f:
            f.write(str(time.time()))
    else:
        print("No new changes detected.")

if __name__ == "__main__":
    check_and_index()
