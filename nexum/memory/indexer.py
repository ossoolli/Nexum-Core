import os
import json
from core.memory.sovereign_memory import SovereignMemory

def index_project_to_memory():
    memory = SovereignMemory()
    project_dir = "/home/madarmutaz/Nexum-Core"
    
    # 1. فهرسة ملفات الإعدادات والبروتوكولات
    for root, dirs, files in os.walk(project_dir):
        for file in files:
            if file.endswith(('.py', '.md', '.json', '.yaml')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read(5000) # قراءة أول 5000 حرف
                        memory.add_memory(f"File_Index_{file}", f"ملف: {file_path}. المحتوى المختصر: {content[:500]}...")
                except Exception:
                    pass

    # 2. فهرسة سجلات الأخطاء السابقة (التي قمنا بحلها)
    log_dir = os.path.join(project_dir, "storage/logs")
    if os.path.exists(log_dir):
        for log in os.listdir(log_dir):
            if log.endswith('.log'):
                memory.add_memory(f"Log_Index_{log}", f"سجل تشغيلي: {log} يحتوي على تاريخ الأخطاء السابقة والترميمات.")

    return "✅ تم فهرسة كافة الملفات والسجلات في الذاكرة السيادية."

if __name__ == "__main__":
    print(index_project_to_memory())
