import time
import os
import sys

def boot_sovereign_core():
    print("--- [INITIALIZING NEXUM CORE OS v3.5.0] ---")
    print("[STATUS]: 18/18 Protocols Loaded.")
    print("[STATUS]: Autonomy: ENABLED.")
    
    try:
        sys.path.append(os.path.abspath(os.path.dirname(__file__)))
        from main_v5 import gemini_service
        root_agent = gemini_service
    except ImportError:
        print("❌ [ERROR]: لم يتم العثور على gemini_service في ملف main_v5.py.")
        sys.exit(1)

    while True:
        try:
            current_time = time.strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{current_time}] - Starting Protocol: [Self-Audit]")
            response, _ = root_agent.ask("قم بمسح دوري (Self-Audit) وتنبيهي بأي خلل في الـ 18 بروتوكول.")
            print(f"[AUDIT RESPONSE]: {response}")
        except Exception as e:
            print(f"⚠️ [WARNING]: تعذر إتمام الفحص الدوري: {e}")
            
        time.sleep(3600)

if __name__ == "__main__":
    boot_sovereign_core()
