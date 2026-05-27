# -*- coding: utf-8 -*-
"""
🔱 GoCoordinatorBridge — جسر التنسيق الفائق بين Go و Python
===================================================
يوفر واجهة برمجية للتحكم بالمنسق بلغة Go وتشغيل خادم الويب الخدمي في الخلفية.
يتواصل مع خادم Go REST/JSON فائق السرعة ويرجع قرارات إجماع مجلس الحكماء.
يتضمن صموداً تلقائياً بالاعتماد على محاكاة محلية في حال تعذر تشغيل الخادم.
"""

import os
import sys
import subprocess
import json
import logging
import time
import socket
import requests
from typing import Dict, Any

logger = logging.getLogger("nexum.go_coordinator")

# مسارات الملفات
CORE_DIR = os.path.dirname(os.path.abspath(__file__))
GO_SOURCE = os.path.join(CORE_DIR, "coordinator.go")
GO_BINARY = os.path.join(CORE_DIR, "coordinator.exe" if os.name == "nt" else "coordinator")

class GoCoordinatorBridge:
    def __init__(self, port: int = 50051):
        self.source_path = GO_SOURCE
        self.binary_path = GO_BINARY
        self.port = port
        self.server_url = f"http://localhost:{self.port}"
        self.server_process = None
        
        # التأكد من بناء وبدء تشغيل السيرفر في الخلفية
        self._ensure_server_running()

    def _is_port_open(self) -> bool:
        """يتحقق ما إذا كان منفذ السيرفر مفتوحاً ومستجيباً بالفعل."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.3)
                return s.connect_ex(("localhost", self.port)) == 0
        except Exception:
            return False

    def _ensure_binary(self) -> bool:
        """يتحقق من وجود الملف التنفيذي، وإذا لم يكن موجوداً يحاول بناؤه."""
        if os.path.exists(self.binary_path):
            return True

        if not os.path.exists(self.source_path):
            logger.error(f"[Go Bridge] Go source file not found at: {self.source_path}")
            return False

        logger.info("[Go Bridge] Executable not found. Attempting to build from source...")
        try:
            # التحقق من وجود Go
            go_check = subprocess.run(
                ["go", "version"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )
            if go_check.returncode != 0:
                logger.warning("[Go Bridge] Go compiler not found in system PATH. Cannot compile from source.")
                return False

            # بناء الملف التنفيذي
            build_cmd = ["go", "build", "-o", self.binary_path, self.source_path]
            logger.info(f"[Go Bridge] Running: {' '.join(build_cmd)}")
            build_run = subprocess.run(
                build_cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True,
                cwd=CORE_DIR
            )
            if build_run.returncode == 0:
                logger.info("[Go Bridge] Build successful!")
                return True
            else:
                logger.error(f"[Go Bridge] Go build failed: {build_run.stderr}")
                return False
        except Exception as e:
            logger.error(f"[Go Bridge] Exception during build: {e}")
            return False

    def _ensure_server_running(self) -> bool:
        """يتحقق من تشغيل سيرفر Go في الخلفية، ويقوم بتشغيله إذا لم يكن نشطاً."""
        if self._is_port_open():
            logger.info(f"[Go Bridge] Live REST Go server already running on port {self.port}.")
            return True

        if not self._ensure_binary():
            logger.warning("[Go Bridge] Go binary unavailable. Bridge will run in simulation fallback.")
            return False

        logger.info(f"[Go Bridge] Launching REST Go server on port {self.port} in the background...")
        try:
            # تشغيل خادم Go في الخلفية مع تمرير المنافذ
            cmd = [
                self.binary_path,
                "-server",
                "-port", str(self.port),
                "-redis", os.getenv("REDIS_ADDR", "localhost:6379")
            ]
            
            # تشغيل السيرفر كعملية مستقلة في الخلفية (Daemon Process)
            # باستخدام flags مخصصة لويندوز لعدم فتح نافذة كونسول جديدة
            creation_flags = 0
            if os.name == "nt":
                creation_flags = 0x08000000  # CREATE_NO_WINDOW
                
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=CORE_DIR,
                creationflags=creation_flags
            )
            
            # الانتظار حتى يبدأ السيرفر بالاستجابة (الحد الأقصى: 3 ثوانٍ)
            for _ in range(15):
                time.sleep(0.2)
                if self._is_port_open():
                    logger.info(f"[Go Bridge] Live REST Go server successfully spawned on port {self.port}.")
                    return True
            
            logger.error("[Go Bridge] REST Go server spawned but failed to bind to port in time.")
            return False
            
        except Exception as e:
            logger.error(f"[Go Bridge] Exception while starting Go server: {e}")
            return False

    def execute_task(self, task: str, threshold: float = 0.3) -> dict:
        """
        يرسل المهمة إلى منسق Go الموزع ويجلب النتيجة المنسقة كـ dict.
        يتواصل مع السيرفر عبر HTTP REST.
        """
        # التأكد من جاهزية السيرفر قبل الإرسال
        server_ready = self._ensure_server_running()
        
        if not server_ready:
            logger.warning("[Go Bridge] Go REST server offline. Falling back to local Python mock simulation.")
            return self._execute_fallback_simulation(task, threshold)

        try:
            # تجهيز المقترحات لمحاكاة الوكلاء (المهندسين)
            proposals = [
                {
                    "agent_id": "Agent-Arch",
                    "role": "Software Architect",
                    "task_id": "live-consensus-task",
                    "code_payload": f"[Software Architect] optimized code for: '{task}'",
                    "risk_assessment": 0.1
                },
                {
                    "agent_id": "Agent-Rapid-Dev",
                    "role": "Rapid Developer",
                    "task_id": "live-consensus-task",
                    "code_payload": f"[Rapid Developer] fast prototype for: '{task}'",
                    "risk_assessment": 0.45
                },
                {
                    "agent_id": "Agent-Security-QA",
                    "role": "Security & QA Auditor",
                    "task_id": "live-consensus-task",
                    "code_payload": f"[Security Auditor] bulletproof architecture for: '{task}'",
                    "risk_assessment": 0.05
                }
            ]

            payload = {
                "task_id": f"task_{int(time.time())}",
                "proposals": proposals,
                "max_risk_threshold": threshold
            }

            # إرسال الطلب للسيرفر الموزع
            response = requests.post(
                f"{self.server_url}/evaluate_consensus",
                json=payload,
                timeout=2.0
            )

            if response.status_code == 200:
                res_data = response.json()
                
                # تهيئة وتعديل خريطة المخرجات لتناسب تماماً البنية المطلوبة بالنظام
                approved_agent = res_data.get("approved_agent_id", "") or "N/A"
                approved_payload = res_data.get("approved_payload", "") or "N/A"
                evaluated_risk = res_data.get("evaluated_risk", 1.0)
                
                return {
                    "consensus_reached": res_data.get("consensus_reached", False),
                    "system_metrics": res_data.get("audit_logs", ""),
                    "approved_proposal": {
                        "agent_id": approved_agent,
                        "solution": approved_payload,
                        "risk_score": evaluated_risk
                    }
                }
            else:
                logger.error(f"[Go Bridge] Server error response {response.status_code}: {response.text}")
                return self._execute_fallback_simulation(task, threshold)

        except Exception as e:
            logger.error(f"[Go Bridge] Connection failed, switching to fallback simulation. Error: {e}")
            return self._execute_fallback_simulation(task, threshold)

    def _execute_fallback_simulation(self, task: str, threshold: float) -> dict:
        """محاكاة محلية مرنة في حال انقطاع السيرفر لضمان صمود النظام"""
        logger.info("[Go Bridge] Fallback simulation deliberating locally...")
        
        # اختيار الخيار الأكثر أماناً بناءً على حد الأمان الممرر
        risk = 0.05
        if risk <= threshold:
            return {
                "consensus_reached": True,
                "system_metrics": f"Consensus reached on Agent [Agent-Security-QA] proposal. Risk level: {risk} (Python local simulation)",
                "approved_proposal": {
                    "agent_id": "Agent-Security-QA",
                    "solution": f"[Security Auditor] bulletproof architecture for: '{task}' (fallback)",
                    "risk_score": risk
                }
            }
        
        return {
            "consensus_reached": False,
            "system_metrics": "All proposals rejected due to high security risk profiles (Python local simulation).",
            "approved_proposal": {
                "agent_id": "N/A",
                "solution": "N/A",
                "risk_score": 1.0
            }
        }

    def close(self):
        """إغلاق سيرفر الخلفية عند استدعائه للتنظيف"""
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=2)
                logger.info("[Go Bridge] REST Go server background process terminated cleanly.")
            except Exception:
                pass

# Singleton
go_coordinator = GoCoordinatorBridge()

if __name__ == "__main__":
    # اختبار تشغيل سريع للخدمة
    print("Testing Live GoCoordinatorBridge...")
    try:
        res = go_coordinator.execute_task("Deploy high-availability Kubernetes cluster on GCP", 0.3)
        print(json.dumps(res, indent=4, ensure_ascii=False))
    finally:
        go_coordinator.close()
