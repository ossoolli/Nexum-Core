# -*- coding: utf-8 -*-
"""
core/memory/components.py
المكونات الفرعية المعزولة للذاكرة السيادية لنظام Nexum Pro
===========================================================
- InfrastructureMap: خريطة حية لبنية المستخدم التحتية
- DecisionMemory: ذاكرة أنماط القرارات والتوقع السلوكي
- MissionLog: سجل المأموريات والدروس المستفادة
"""

import os
import json
import uuid
import platform
from datetime import datetime
from typing import Optional, List, Dict, Any

# التحقق من وجود psutil وإلا الاعتماد على قيم افتراضية دفاعية
try:
    import psutil
except ImportError:
    psutil = None

# استيراد مخزن الحفظ الذري من النواة (أو Fallback محلي)
try:
    from core.memory_local import AtomicJSONStore
except ImportError:
    import threading

    class AtomicJSONStore:
        """مخزن ذري محلي Fallback لمنع تلف الملفات."""
        def __init__(self, filepath: str):
            self.filepath = os.path.realpath(filepath)
            self.lock = threading.Lock()

        def load(self, default_factory) -> Any:
            with self.lock:
                try:
                    if os.path.exists(self.filepath):
                        with open(self.filepath, 'r', encoding='utf-8') as f:
                            return json.load(f)
                except Exception as e:
                    print(f"[WATCHDOG ERROR] Failed to read '{self.filepath}': {e}")
                return default_factory()

        def save(self, data: Any) -> bool:
            with self.lock:
                temp_file = None
                try:
                    os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
                    temp_file = self.filepath + f".{uuid.uuid4().hex[:8]}.tmp"
                    with open(temp_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
                    os.replace(temp_file, self.filepath)
                    return True
                except Exception as e:
                    print(f"[WATCHDOG ERROR] Atomic save failed on '{self.filepath}': {e}")
                    if temp_file and os.path.exists(temp_file):
                        try:
                            os.remove(temp_file)
                        except OSError:
                            pass
                    return False

# ─── حدود الأمان المشتركة ───
MAX_TEXT_LENGTH = 2000
MAX_RECORDS = 500


# ═══════════════════════════════════════════════════════════
# 1. InfrastructureMap — خريطة البنية التحتية
# ═══════════════════════════════════════════════════════════

class InfrastructureMap:
    """
    خريطة حية لبنية المستخدم التحتية.
    تُبنى مرة وتُحدَّث تلقائيا عند كل تغيير في بيئة السيرفر والمشاريع.
    """

    def __init__(self, storage_path: str):
        self.store = AtomicJSONStore(storage_path)
        self.map: dict = self.store.load(dict)

    def scan_and_build(self) -> None:
        """يمسح البيئة الحالية ويبني الخريطة التقنية كاملة."""
        print("[Sovereign Memory] Starting infrastructure auto-scan and mapping...")
        self.map = {
            "servers": self._scan_servers(),
            "projects": self._scan_projects(),
            "priorities": self.map.get("priorities", []),
            "custom_delegation_rules": self.map.get("custom_delegation_rules", []),
            "trust_matrix": self.map.get("trust_matrix", {}),
            "experience_pool": self.map.get("experience_pool", []),
            "discovered_patterns": self.map.get("discovered_patterns", []),
            "last_updated": datetime.now().isoformat()
        }
        self.store.save(self.map)
        print(f"[Sovereign Memory] Infrastructure mapping complete. Scanned {len(self.map['projects'])} projects.")

    def update_field(self, key: str, value: Any) -> None:
        """تحديث حقل برمجي محدد وحفظ التعديلات فورا وبشكل ذري."""
        self.map[key] = value
        self.map["last_updated"] = datetime.now().isoformat()
        self.store.save(self.map)

    def _scan_servers(self) -> dict:
        """مسح مواصفات الجهاز والعتاد لبناء خريطة البيئة التشغيلية."""
        ram_gb = 0.0
        disk_gb = 0.0
        if psutil:
            try:
                ram_gb = round(psutil.virtual_memory().total / 1e9, 1)
                # استخدام '.' للتوافق مع Windows (بدل '/')
                disk_gb = round(psutil.disk_usage('.').total / 1e9, 1)
            except Exception:
                pass

        return {
            "hostname": platform.node(),
            "os": platform.system(),
            "arch": platform.machine(),
            "cpu_cores": os.cpu_count(),
            "ram_gb": ram_gb,
            "disk_gb": disk_gb,
            "python_version": platform.python_version()
        }

    def _scan_projects(self) -> list:
        """يبحث عن مشاريع Git في بيئة عمل المستخدم مع حد عمق لحماية الأداء."""
        projects = []
        home = os.path.expanduser("~")
        max_depth = 4
        skip_dirs = {
            '__pycache__', 'node_modules', 'venv', 'env', '.venv',
            'build', 'dist', '.tox', '.mypy_cache', '.git'
        }

        try:
            for root, dirs, files in os.walk(home):
                # استبعاد المجلدات الضخمة والمخفية
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in skip_dirs]

                # تقييد العمق لتفادي تعليق المعالج
                depth = root.replace(home, '').count(os.sep)
                if depth > max_depth:
                    dirs.clear()
                    continue

                if '.git' in os.listdir(root):
                    projects.append({
                        "name": os.path.basename(root),
                        "path": os.path.realpath(root),
                        "type": self._detect_project_type(root)
                    })
        except Exception as e:
            print(f"[WATCHDOG ERROR] Project scan interrupted: {e}")
        return projects

    def _detect_project_type(self, root_path: str) -> str:
        """الكشف الذكي عن نوع المشروع بناء على الملفات الجذرية."""
        try:
            files = os.listdir(root_path)
            if "package.json" in files:
                return "Node.js / JavaScript"
            if "requirements.txt" in files or "pyproject.toml" in files:
                return "Python"
            if "go.mod" in files:
                return "Go"
            if "Cargo.toml" in files:
                return "Rust"
            if "pom.xml" in files:
                return "Java / Maven"
            if "build.gradle" in files:
                return "Java / Gradle"
        except Exception:
            pass
        return "Generic Git Repo"


# ═══════════════════════════════════════════════════════════
# 2. DecisionMemory — ذاكرة أنماط القرارات
# ═══════════════════════════════════════════════════════════

class DecisionMemory:
    """يحفظ أنماط قرارات المستخدم ويستخدمها لتوقع تفضيلاته المستقبلية."""

    def __init__(self, storage_path: str):
        self.store = AtomicJSONStore(storage_path)
        self.decisions: list = self.store.load(list)

    def record_decision(self, situation: str, nexum_suggestion: str,
                        user_response: str, user_modification: str = None) -> None:
        """تسجيل قرار مع استخلاص الأنماط المفتاحية وحماية ضد تضخم النصوص."""
        entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "situation": (situation or "")[:MAX_TEXT_LENGTH],
            "suggestion": (nexum_suggestion or "")[:MAX_TEXT_LENGTH],
            "response": user_response,  # approved / rejected / modified
            "modification": (user_modification or "")[:MAX_TEXT_LENGTH] if user_modification else None,
            "pattern_tags": self._extract_patterns(situation or "")
        }
        self.decisions.append(entry)

        # حصر المخزن بأحدث MAX_RECORDS قرار فقط
        self.decisions = self.decisions[-MAX_RECORDS:]
        self.store.save(self.decisions)

    def predict_preference(self, new_situation: str) -> dict:
        """التنبؤ بنسبة تفضيل المستخدم بناء على تشابه الأنماط المسجلة."""
        current_tags = self._extract_patterns(new_situation)
        if not current_tags or not self.decisions:
            return {"confidence": 0.0, "prediction": "unknown", "based_on_samples": 0}

        similar = [d for d in self.decisions
                   if any(t in d.get("pattern_tags", []) for t in current_tags)]
        if not similar:
            return {"confidence": 0.0, "prediction": "unknown", "based_on_samples": 0}

        approvals = sum(1 for s in similar if s["response"] == "approved")
        confidence = approvals / len(similar)

        return {
            "confidence": round(confidence, 2),
            "prediction": "approve" if confidence >= 0.7 else "reject",
            "based_on_samples": len(similar)
        }

    def _extract_patterns(self, text: str) -> list:
        """خوارزمية أولية لاستخلاص الكلمات المفتاحية السياقية."""
        keywords = [
            "prod", "dev", "git", "docker", "restart", "delete", "env",
            "database", "backup", "nginx", "pm2", "install", "deploy",
            "build", "test", "config", "update", "create", "push"
        ]
        text_lower = text.lower() if text else ""
        return [kw for kw in keywords if kw in text_lower]


# ═══════════════════════════════════════════════════════════
# 3. MissionLog — سجل المأموريات
# ═══════════════════════════════════════════════════════════

class MissionLog:
    """سجل كامل للمأموريات المنفذة لمنع تكرار الأخطاء وتسجيل الدروس المستفادة."""

    def __init__(self, storage_path: str):
        self.store = AtomicJSONStore(storage_path)
        self.log: list = self.store.load(list)

    def log_mission(self, goal: str, plan: list = None, result: str = "success",
                    duration_seconds: float = 0.0, lessons: str = None) -> None:
        """تسجيل مأمورية برمجية مع دروسها المستفادة وحماية ضد تضخم النصوص."""
        entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "goal": (goal or "")[:MAX_TEXT_LENGTH],
            "plan_steps": [str(step)[:500] for step in (plan or [])][:20],
            "result": result,  # success / failed
            "duration": round(duration_seconds, 2),
            "lessons_learned": (lessons or "No critical failures observed.")[:MAX_TEXT_LENGTH]
        }
        self.log.append(entry)

        # حصر المخرجات بأحدث MAX_RECORDS مأمورية
        self.log = self.log[-MAX_RECORDS:]
        self.store.save(self.log)

    def get_lessons_for(self, goal_type: str) -> list:
        """استرجاع الدروس المستفادة المرتبطة بنوع المأمورية المستهدفة."""
        similar_lessons = []
        for mission in self.log:
            if goal_type.lower() in mission.get("goal", "").lower():
                lesson = mission.get("lessons_learned")
                if lesson and "No critical failures" not in lesson:
                    similar_lessons.append(lesson)
        return similar_lessons[:5]

    def get_success_rate(self) -> dict:
        """حساب نسبة النجاح الكلية للمأموريات التاريخية."""
        total = len(self.log)
        if total == 0:
            return {"total": 0, "success_rate": 0.0}
        successes = sum(1 for m in self.log if m.get("result") == "success")
        return {
            "total": total,
            "successes": successes,
            "failures": total - successes,
            "success_rate": round(successes / total, 3)
        }
