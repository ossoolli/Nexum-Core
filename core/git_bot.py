import subprocess
import os
from core.system_tools import BASE_DIR

def auto_sync():
    try:
        path = BASE_DIR
        os.chdir(path)
        # فرض الإضافة والتسجيل بدون أي تفاعل بشري
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "NEXUM_AUTO_PULSE_SYNC", "--no-edit"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("🚀 [GitBot] Global Sync Complete.")
    except Exception as e:
        print(f"⚠️ [GitBot] Silent Sync: {e}")

if __name__ == "__main__":
    auto_sync()
