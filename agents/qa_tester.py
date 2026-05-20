import os
import requests
import time

def check_app_health(port, app_name):
    """يفحص صحة التطبيق عبر البورت الخاص به"""
    try:
        response = requests.get(f"http://localhost:{port}", timeout=5)
        if response.status_code == 200:
            return f"✅ {app_name} is ALIVE and responding."
        return f"⚠️ {app_name} returned status {response.status_code}."
    except Exception as e:
        return f"❌ {app_name} is unreachable on port {port}."

def verify_file_production(path):
    """يتأكد أن التطبيق قام بإنتاج ملفات النتائج"""
    if os.path.exists(path):
        size = os.path.getsize(path)
        return f"✅ Result file found: {path} ({size} bytes)"
    return f"❌ Result file NOT FOUND at: {path}"

if __name__ == "__main__":
    # اختبار تطبيق الحاسبة على سبيل المثال
    from core.system_tools import BASE_DIR
    print("🔍 [QA-Tester] Starting diagnostics...")
    print(check_app_health(8081, "NASA-App"))
    print(verify_file_production(os.path.join(BASE_DIR, "registry", "apps", "advanced_calculator", "results.txt")))
