import os
import importlib.util
import logging
import threading
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from core.tool_registry import tool_registry

logger = logging.getLogger(__name__)

class PluginHandler(FileSystemEventHandler):
    """معالج أحداث لملفات المجلد المراقب"""
    def __init__(self, loader):
        self.loader = loader

    def on_created(self, event):
        if not event.is_directory and str(event.src_path).endswith('.py'):
            self.loader.load_plugin(event.src_path)

class DynamicPluginLoader:
    """نظام تحميل الإضافات الديناميكي"""
    def __init__(self, plugins_dir="/home/madarmutaz/Nexum-Core/plugins/active"):
        self.plugins_dir = plugins_dir
        os.makedirs(self.plugins_dir, exist_ok=True)
        self.loaded_plugins = {}

    def load_all_existing(self):
        """تحميل كل الملفات الموجودة عند البدء"""
        for filename in os.listdir(self.plugins_dir):
            if filename.endswith(".py"):
                path = os.path.join(self.plugins_dir, filename)
                self.load_plugin(path)

    def load_plugin(self, file_path):
        """استيراد ملف بايثون وتسجيل الأدوات فيه"""
        try:
            module_name = os.path.basename(file_path).replace(".py", "")
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # البحث عن الدوال التي تبدأ بـ 'tool_' أو المصنفة كأدوات
            count = 0
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if callable(attr) and attr_name.startswith("tool_"):
                    tool_registry.register_local_tool(attr_name, attr)
                    count += 1
            
            self.loaded_plugins[module_name] = count
            logger.info(f"🔌 Loaded plugin '{module_name}' with {count} tools.")
            return True
        except Exception as e:
            logger.error(f"Failed to load plugin {file_path}: {e}")
            return False

    def start_watching(self):
        """بدء مراقبة المجلد في خلفية منفصلة"""
        def _watch():
            event_handler = PluginHandler(self)
            observer = Observer()
            observer.schedule(event_handler, self.plugins_dir, recursive=False)
            observer.start()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
            observer.join()

        thread = threading.Thread(target=_watch, daemon=True)
        thread.start()
        logger.info(f"👀 Watching plugins directory: {self.plugins_dir}")

plugin_loader = DynamicPluginLoader()
