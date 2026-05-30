import sys
import os
# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import json
from core.memory.sovereign_memory import SovereignMemory

def index_project_to_memory():
    memory = SovereignMemory()
    project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    print("🔍 بدء عملية فهرسة ملفات الكود والمشروع...")
    
    # 1. فهرسة ملفات الإعدادات والبروتوكولات (تخطي المجلدات الكبيرة وغير المهمة لعدم التعليق)
    ignore_dirs = {'venv', '.git', '__pycache__', '.pytest_cache', '.claude', 'Nexum-Core', 'home', 'storage', 'skills', 'optional-skills'}
    indexed_files_count = 0
    
    for root, dirs, files in os.walk(project_dir):
        # تعديل المجلدات في مكانها لتفادي الدخول للمجلدات المستبعدة
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            if file.endswith(('.py', '.md', '.json', '.yaml', '.yml', '.conf', '.ini')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read(3000) # قراءة أول 3000 حرف
                        if content.strip():
                            memory.add_memory(
                                f"File_Index_{file}", 
                                f"الملف البرمجي: {file_path}\n"
                                f"المحتوى التعريفي:\n{content[:1500]}..."
                            )
                            indexed_files_count += 1
                except Exception:
                    pass

    print(f"✅ تم فهرسة {indexed_files_count} ملف كود في الذاكرة السيادية.")
    print("🔍 بدء فهرسة وقراءة سجلات النظام (Logs)...")

    # 2. فهرسة سجلات الأخطاء والسجلات التشغيلية لتسهيل الاسترجاع والترميم الذاتي
    log_dir = os.path.join(project_dir, "storage/logs")
    indexed_logs_count = 0
    
    if os.path.exists(log_dir):
        # البحث عن كافة ملفات السجلات، حتى في المجلدات الفرعية للسجلات
        for root, dirs, files in os.walk(log_dir):
            for file in files:
                if file.endswith('.log'):
                    log_path = os.path.join(root, file)
                    try:
                        with open(log_path, 'r', encoding='utf-8') as f:
                            # قراءة آخر 4000 حرف من ملف السجل للحصول على السجلات والتحذيرات التشغيلية الأخيرة
                            f.seek(0, os.SEEK_END)
                            size = f.tell()
                            read_size = min(size, 8000) # قراءة آخر 8 كيلوبايت
                            f.seek(max(0, size - read_size))
                            content = f.read(read_size)
                            
                            if content.strip():
                                memory.add_memory(
                                    f"Log_Index_{file}", 
                                    f"ملف السجل التشغيلي: {log_path}\n"
                                    f"السياق والأخطاء التشغيلية المرصودة:\n{content}..."
                                )
                                indexed_logs_count += 1
                    except Exception as e:
                        print(f"⚠️ خطأ أثناء قراءة السجل {file}: {e}")
                        pass

    print(f"✅ تم قراءة وفهرسة {indexed_logs_count} ملف سجلات تشغيلية بنجاح.")
    return f"🚀 تم دمج {indexed_files_count} ملفات برمجة و {indexed_logs_count} ملفات سجلات تشغيلية في الذاكرة الدائمة لـ Nexum-Core."

if __name__ == "__main__":
    print(index_project_to_memory())
