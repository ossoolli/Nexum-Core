# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import json
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
            status_dict[name] = {"status": status, "restarts": restarts}
        return status_dict
    except Exception as e:
        return {"error": str(e)}

def test_gemini_vertex():
    # Set standard env variables
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/madarmutaz/Nexum-Core/storage/gcp_key.json"
    os.environ["GOOGLE_CLOUD_PROJECT"] = "mytest-496209"
    os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
    
    try:
        from google import genai
        from google.genai.types import HttpOptions
        client = genai.Client(http_options=HttpOptions(api_version="v1"))
        # Quick check with a minimal prompt
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="test"
        )
        if response.text:
            return {"status": "success", "message": "Gemini Vertex AI is connected and healthy."}
        else:
            return {"status": "warning", "message": "Empty response from Gemini Vertex AI."}
    except Exception as e:
        return {"status": "failed", "message": str(e)}

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

def main():
    print("🔍 **بدء فحص الرقابة الذاتية لـ Nexum-Core...**")
    print(f"الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 40)
    
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
                pm2_report.append(f"🔴 الخدمة **{s}** ليست متصلة! الحالة الحالية: `{info.get('status')}` (إعادة تشغيل: {info.get('restarts')})")
                services_ok = False
            elif isinstance(info, dict):
                pm2_report.append(f"🟢 الخدمة **{s}** تعمل بشكل طبيعي (إعادة تشغيل: {info.get('restarts')})")
                
    # 2. Gemini Vertex AI Test
    gemini_test = test_gemini_vertex()
    
    # 3. Log Error Scan
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
            
    # Output report
    print("\n📊 **تقرير البنية التحتية والخدمات:**")
    for r in pm2_report:
        print(r)
        
    print("\n🧠 **حالة الذكاء الاصطناعي (Gemini Vertex AI):**")
    if gemini_test["status"] == "success":
        print(f"🟢 {gemini_test['message']}")
    else:
        print(f"🔴 فشل الاتصال بـ Gemini Vertex AI: `{gemini_test['message']}`")
        
    if log_errors:
        print("\n⚠️ **أخطاء تم رصدها في السجلات مؤخراً:**")
        for log_name, errs in log_errors.items():
            print(f"🔹 **{log_name}:**")
            for e in errs:
                print(f"   - `{e}`")
    else:
        print("\n🟢 لا توجد أخطاء حرجة جديدة في السجلات.")
        
    print("\n" + "=" * 40)
    
    # Exit codes indicating state
    if not services_ok or gemini_test["status"] != "success":
        print("🚨 **النتيجة: تم رصد مشكلة تتطلب التدخل أو الإصلاح التلقائي!**")
        sys.exit(1)
    else:
        print("✅ **النتيجة: جميع الأنظمة تعمل بكفاءة تامة وسعادة!**")
        sys.exit(0)

if __name__ == "__main__":
    main()
