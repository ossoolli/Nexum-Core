"""
core/fs_context.py
يُولّد سياقاً مفهوماً للـ AI عن بنية المشروع
هذه "عيون" NEXUM — يرى ثم يقرر
"""
import os
from datetime import datetime
from core.env_config import BASE_DIR, WORKSPACE_DIR, PROJECT_ROOT
from core.fs_navigator import fs_navigator
from core.fs_search import fs_search
from core.fs_control import fs_control


class FSContext:
    """
    يُولّد وصفاً نصياً/JSON لبنية الملفات
    يُرسَل لـ Gemini كـ context قبل اتخاذ قرار
    """

    def __init__(self):
        self.base = BASE_DIR

    def project_snapshot(self, max_depth: int = 2) -> dict:
        """
        يأخذ لقطة كاملة عن المشروع:
        - هيكل المجلدات
        - الملفات الأحدث تعديلاً
        - الملفات الأكبر حجماً
        - ملخص اللغات المستخدمة
        """
        tree = fs_navigator.tree(self.base, max_depth=max_depth)
        recent = fs_search.recent(self.base, days=3, limit=10)
        large = fs_search.by_size(self.base, min_kb=10, sort_desc=True)

        # حساب اللغات
        lang_count = {}
        for dirpath, _, files in os.walk(self.base):
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext:
                    lang_count[ext] = lang_count.get(ext, 0) + 1

        top_langs = sorted(lang_count.items(), key=lambda x: x[1], reverse=True)[:8]

        return {
            "success": True,
            "project_root": self.base,
            "snapshot_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "structure": tree.get('tree', ''),
            "recent_files": recent.get('results', []),
            "large_files": large.get('results', [])[:10],
            "language_distribution": dict(top_langs),
            "total_files": tree.get('total_files', 0),
            "total_dirs": tree.get('total_dirs', 0)
        }

    def file_context(self, path: str) -> dict:
        """
        يُعطي سياقاً كاملاً لملف واحد:
        - المحتوى
        - الملفات المجاورة
        - الملفات التي تستورده
        """
        read_result = fs_control.read_file(path)
        if not read_result['success']:
            return read_result

        data = read_result['data']

        # الملفات في نفس المجلد
        parent_dir = os.path.dirname(data['path'])
        siblings = fs_navigator.ls(parent_dir)

        # من يستورد هذا الملف؟ (للـ Python)
        filename_no_ext = os.path.splitext(os.path.basename(path))[0]
        importers = []
        if path.endswith('.py'):
            search_result = fs_search.by_content(
                f"import {filename_no_ext}",
                root=self.base,
                extensions=['.py']
            )
            importers = [r['file'] for r in search_result.get('results', [])]

        return {
            "success": True,
            "file": data,
            "siblings": siblings.get('files', [])[:10] if siblings['success'] else [],
            "imported_by": importers[:5],
            "ai_summary_hint": (
                f"الملف {path} يحتوي {data['total_lines']} سطر، "
                f"حجمه {data['size_kb']}KB، "
                f"آخر تعديل {data['modified']}."
            )
        }

    def format_for_ai(self, context: dict, max_chars: int = 3000) -> str:
        """
        يُنسّق السياق كنص واضح يُرسَل لـ Gemini
        """
        if not context.get('success'):
            return f"خطأ في السياق: {context.get('error', 'غير معروف')}"

        lines = []

        if 'structure' in context:
            lines.append("=== بنية المشروع ===")
            lines.append(context['structure'][:1000])

        if 'file' in context:
            f = context['file']
            lines.append(f"=== الملف: {f.get('relative', f.get('path'))} ===")
            lines.append(f"الأسطر: {f.get('total_lines')} | الحجم: {f.get('size_kb')}KB")
            lines.append("--- المحتوى ---")
            lines.append(f.get('content', '')[:1500])

        if context.get('imported_by'):
            lines.append(f"\nيُستورَد من: {', '.join(context['imported_by'])}")

        if context.get('recent_files'):
            lines.append("\n=== أحدث الملفات تعديلاً ===")
            for rf in context['recent_files'][:5]:
                lines.append(f"• {rf['file']} ({rf['modified']})")

        result = "\n".join(lines)
        return result[:max_chars]


fs_context = FSContext()
