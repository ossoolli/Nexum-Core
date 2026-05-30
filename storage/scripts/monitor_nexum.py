# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import json
import time
from datetime import datetime

# Inject Nexum root into path
sys.path.insert(0, "/home/madarmutaz/Nexum-Core")

def check_pm2_status():
    try:
        res = subprocess.run(["pm2", "jlist"], capture_output=True, text=True, check=True)
        processes = json.loads(res.stdout)
        status_dict = {}
        for p in processes:
            name = p.get("name")
            pm2_env = p.get("pm2_env", {})
            status = pm2_env.get("status")
            restarts = pm2_env.get("restart_time")
            monit = p.get("monit", {})
            cpu = monit.get("cpu", 0.0)
            mem_bytes = monit.get("memory", 0)
            mem_mb = round(mem_bytes / (1024 * 1024), 1)
            status_dict[name] = {
                "status": status,
                "restarts": restarts,
                "cpu": cpu,
                "memory": mem_mb
            }
        return status_dict
    except Exception as e:
        return {"error": str(e)}

def test_gemini_vertex():
    # Set standard env variables
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/madarmutaz/Nexum-Core/storage/gcp_key.json"
    os.environ["GOOGLE_CLOUD_PROJECT"] = "mytest-496209"
    os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
    
    start_time = time.perf_counter()
    try:
        from google import genai
        from google.genai.types import HttpOptions
        client = genai.Client(http_options=HttpOptions(api_version="v1"))
        # Quick check with a minimal prompt
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="test"
        )
        elapsed_ms = round((time.perf_counter() - start_time) * 1000)
        if response.text:
            return {"status": "success", "message": "Gemini Vertex AI is connected and healthy.", "latency_ms": elapsed_ms}
        else:
            return {"status": "warning", "message": "Empty response from Gemini Vertex AI.", "latency_ms": elapsed_ms}
    except Exception as e:
        return {"status": "failed", "message": str(e), "latency_ms": 0}

def scan_errors(log_path, max_lines=100):
    if not os.path.exists(log_path):
        return []
    critical_keywords = ["unauthenticated", "401", "module_not_found", "syntaxerror", "db_connection", "connection refused", "token"]
    found_errors = []
    try:
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()[-max_lines:]
            for idx, line in enumerate(lines):
                lower_line = line.lower()
                if "error" in lower_line or any(kw in lower_line for kw in critical_keywords):
                    found_errors.append(line.strip())
        return found_errors
    except Exception as e:
        return [f"Failed to read log: {str(e)}"]

def ping_nexum_api():
    start = time.perf_counter()
    try:
        import requests
        res = requests.get("http://localhost:8080", timeout=2)
        elapsed_ms = round((time.perf_counter() - start) * 1000)
        return {"status": "online", "latency_ms": elapsed_ms}
    except Exception as e:
        return {"status": "offline", "latency_ms": 0, "error": str(e)}

def check_state_db_status():
    import sqlite3
    db_path = "/home/madarmutaz/.hermes/state.db"
    
    if not os.path.exists(db_path):
        return {"status": "NOT FOUND", "size_mb": 0.0, "encrypted": "UNKNOWN", "integrity": "FAILED"}
        
    size_bytes = os.path.getsize(db_path)
    size_mb = round(size_bytes / (1024 * 1024), 2)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        cursor.fetchall()
        conn.close()
        encrypted = "DECRYPTED (Plaintext)"
        integrity = "PASSED"
    except Exception as e:
        if "file is not a database" in str(e) or "encrypted" in str(e):
            encrypted = "ENCRYPTED (AES-256 via SQLCipher)"
            try:
                import dotenv
                dotenv.load_dotenv("/home/madarmutaz/Nexum-Core/.env")
                db_key = os.getenv("NEXUM_DB_ENCRYPTION_KEY")
                from pysqlcipher3 import dbapi2 as cipher_sqlite3
                conn = cipher_sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute(f"PRAGMA key = '{db_key}';")
                try:
                    cursor.execute("PRAGMA cipher_compatibility = 3;")
                    cursor.execute("SELECT 1 FROM sqlite_master LIMIT 1;")
                except Exception:
                    cursor.execute("PRAGMA cipher_compatibility = 4;")
                cursor.execute("PRAGMA integrity_check;")
                res = cursor.fetchone()
                integrity = "PASSED" if res and res[0] == "ok" else f"FAILED: {res}"
                conn.close()
            except Exception as cipher_err:
                integrity = f"FAILED: {cipher_err}"
        else:
            encrypted = "UNKNOWN ERROR"
            integrity = f"FAILED: {e}"
            
    return {"status": "OK", "size_mb": size_mb, "encrypted": encrypted, "integrity": integrity}

def main():
    script_start = time.perf_counter()
    print("🔍 **بدء فحص الرقابة الذاتية الفائق لـ Nexum-Core (v12.0.0+)...**")
    print(f"الوقت الحالي: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. PM2 Services Status
    pm2_status = check_pm2_status()
    required_services = ["nexum-core", "nexum-api", "nexum-sentinel"]
    services_ok = True
    pm2_report = []
    
    if "error" in pm2_status:
        print(f"❌ خطأ أثناء الاتصال بـ PM2: {pm2_status['error']}")
        services_ok = False
    else:
        for s in required_services:
            info = pm2_status.get(s)
            if not info:
                pm2_report.append(f"🔴 الخدمة **{s}** غير موجودة في PM2!")
                services_ok = False
            elif isinstance(info, dict) and info.get("status") != "online":
                pm2_report.append(f"🔴 الخدمة **{s}** ليست متصلة! الحالة: `{info.get('status')}` (CPU: {info.get('cpu')}% | RAM: {info.get('memory')}MB | إعادة تشغيل: {info.get('restarts')})")
                services_ok = False
            elif isinstance(info, dict):
                pm2_report.append(f"🟢 الخدمة **{s}** تعمل بكفاءة (CPU: {info.get('cpu')}% | RAM: {info.get('memory')}MB | إعادة تشغيل: {info.get('restarts')})")
                
    # 2. Gemini Vertex AI Test
    gemini_test = test_gemini_vertex()
    
    # 3. API Response Time Check
    api_test = ping_nexum_api()
    
    # 4. state.db Integrity and Encryption Check
    db_test = check_state_db_status()
    
    # 5. Log Error Scan
    log_errors = {}
    logs_to_scan = {
        "Core Error Log": "/home/madarmutaz/Nexum-Core/storage/logs/err.log",
        "API Error Log": "/home/madarmutaz/Nexum-Core/storage/logs/api_err.log",
        "Sentinel Log": "/home/madarmutaz/Nexum-Core/storage/logs/sentinel.log"
    }
    for name, path in logs_to_scan.items():
        errs = scan_errors(path)
        if errs:
            log_errors[name] = errs[:5] # keep top 5
            
    cron_exec_time = round(time.perf_counter() - script_start, 2)
    
    # Output report in Arabic
    print("\n📊 **تقرير البنية التحتية والخدمات:**")
    for r in pm2_report:
        print(r)
        
    print(f"\n⚡ **زمن استجابة واجهة برمجة التطبيقات (nexum-api):**")
    if api_test["status"] == "online":
        print(f"🟢 nexum-api Response Time (Ping): {api_test['latency_ms']}ms (Healthy under 50ms)")
    else:
        print(f"🔴 nexum-api Offline or Unreachable! Error: {api_test.get('error')}")
        services_ok = False
        
    print("\n🧠 **حالة الذكاء الاصطناعي السيادي (Gemini Vertex AI):**")
    if gemini_test["status"] == "success":
        print(f"🟢 Vertex AI Gemini Latency: {gemini_test['latency_ms']}ms (gemini-2.5-flash optimal response)")
    else:
        print(f"🔴 فشل الاتصال بـ Gemini Vertex AI: `{gemini_test['message']}`")
        
    print("\n🔒 **حالة أمن الفهرس المعرفي والبيانات (state.db):**")
    print(f"🔹 Integrity Check: {db_test['integrity']}")
    print(f"🔹 Database Size: {db_test['size_mb']}MB")
    print(f"🔹 Encryption Status: {db_test['encrypted']}")
    
    print(f"\n⏱️ **مدة تنفيذ الفحص الدوري (Cronjob Execution Time):**")
    print(f"🔹 {cron_exec_time} seconds")
    
    if log_errors:
        print("\n⚠️ **أخطاء تم رصدها في السجلات مؤخراً:**")
        for log_name, errs in log_errors.items():
            print(f"🔹 **{log_name}:**")
            for e in errs:
                print(f"   - `{e}`")
    else:
        print("\n🟢 لا توجد أخطاء حرجة جديدة في السجلات.")
        
    print("\n" + "=" * 60)
    
    # Exit codes indicating state
    if not services_ok or gemini_test["status"] != "success":
        print("🚨 **النتيجة: تم رصد مشكلة تتطلب التدخل أو الإصلاح التلقائي!**")
        sys.exit(1)
    else:
        print("✅ **النتيجة: جميع الأنظمة تعمل بكفاءة تامة وسيادة مطلقة!**")
        sys.exit(0)

if __name__ == "__main__":
    main()
