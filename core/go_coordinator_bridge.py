# -*- coding: utf-8 -*-
"""
🔱 GoCoordinatorBridge — جسر التنسيق بين Go و Python
===================================================
يوفر واجهة برمجية لاستدعاء المنسق الموزع المكتوب بلغة Go من داخل تطبيق Python.
يتحقق من وجود الملف التنفيذي ويقوم ببنائه تلقائياً إذا كان مترجم Go متاحاً.
"""

import os
import sys
import subprocess
import json
import logging

logger = logging.getLogger("nexum.go_coordinator")

# مسارات الملفات
CORE_DIR = os.path.dirname(os.path.abspath(__file__))
GO_SOURCE = os.path.join(CORE_DIR, "coordinator.go")
GO_BINARY = os.path.join(CORE_DIR, "coordinator.exe" if os.name == "nt" else "coordinator")

class GoCoordinatorBridge:
    def __init__(self):
        self.source_path = GO_SOURCE
        self.binary_path = GO_BINARY
        self._ensure_binary()

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
                text=True
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

    def execute_task(self, task: str, threshold: float = 0.3) -> dict:
        """
        يرسل المهمة إلى منسق Go الموزع ويجلب النتيجة المنسقة كـ dict.
        
        Args:
            task: المهمة المطلوب معالجتها
            threshold: الحد الأقصى للمخاطرة المقبولة (0.0 إلى 1.0)
            
        Returns:
            dict: النتيجة المرجعة من المنسق
        """
        if not self._ensure_binary():
            return {
                "consensus_reached": False,
                "system_metrics": "Error: Go coordinator executable is unavailable.",
                "approved_proposal": {"agent_id": "N/A", "solution": "N/A", "risk_score": 1.0}
            }

        try:
            # استدعاء الملف التنفيذي مع التمرير
            cmd = [
                self.binary_path,
                "-task", task,
                "-threshold", str(threshold)
            ]
            
            # تشغيل كعملية فرعية
            run = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8"
            )
            
            if run.returncode != 0:
                logger.error(f"[Go Bridge] Execution failed: {run.stderr}")
                return {
                    "consensus_reached": False,
                    "system_metrics": f"Execution error: {run.stderr}",
                    "approved_proposal": {"agent_id": "N/A", "solution": "N/A", "risk_score": 1.0}
                }

            # تحليل الرد كـ JSON
            output = run.stdout.strip()
            if not output:
                return {
                    "consensus_reached": False,
                    "system_metrics": "Error: Empty response from Go coordinator.",
                    "approved_proposal": {"agent_id": "N/A", "solution": "N/A", "risk_score": 1.0}
                }

            result = json.loads(output)
            if "error" in result:
                return {
                    "consensus_reached": False,
                    "system_metrics": f"Error: {result['error']}",
                    "approved_proposal": {"agent_id": "N/A", "solution": "N/A", "risk_score": 1.0}
                }
                
            return result

        except Exception as e:
            logger.error(f"[Go Bridge] Exception during task execution: {e}")
            return {
                "consensus_reached": False,
                "system_metrics": f"Exception: {str(e)}",
                "approved_proposal": {"agent_id": "N/A", "solution": "N/A", "risk_score": 1.0}
            }

# Singleton
go_coordinator = GoCoordinatorBridge()

if __name__ == "__main__":
    # اختبار سريع للجسر
    print("Testing GoCoordinatorBridge...")
    res = go_coordinator.execute_task("Deploy high-availability Kubernetes cluster on GCP", 0.3)
    print(json.dumps(res, indent=4, ensure_ascii=False))
