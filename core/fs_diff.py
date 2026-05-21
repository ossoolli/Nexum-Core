"""
core/fs_diff.py
مقارنة الملفات والمجلدات ومزامنة الفروقات
"""
import os
import difflib
import filecmp
import shutil
from pathlib import Path
from core.env_config import BASE_DIR
from core.fs_control import fs_control


class FSDiff:
    def __init__(self):
        self.base = BASE_DIR

    def diff_files(self, path_a: str, path_b: str, context_lines: int = 3) -> dict:
        """يقارن ملفين نصيين ويُعيد الفروقات"""
        for path, label in [(path_a, 'A'), (path_b, 'B')]:
            r = fs_control.read_file(path)
            if not r['success']:
                return {"success": False, "error": f"لا يمكن قراءة الملف {label}: {r['error']}"}

        content_a = fs_control.read_file(path_a)['data']['content'].splitlines(keepends=True)
        content_b = fs_control.read_file(path_b)['data']['content'].splitlines(keepends=True)

        diff = list(difflib.unified_diff(
            content_a, content_b,
            fromfile=path_a, tofile=path_b,
            n=context_lines
        ))

        added = sum(1 for l in diff if l.startswith('+') and not l.startswith('+++'))
        removed = sum(1 for l in diff if l.startswith('-') and not l.startswith('---'))

        return {
            "success": True,
            "identical": len(diff) == 0,
            "added_lines": added,
            "removed_lines": removed,
            "diff": "".join(diff[:100]),
            "diff_truncated": len(diff) > 100
        }

    def diff_dirs(self, dir_a: str, dir_b: str) -> dict:
        """يقارن مجلدين ويُعيد قائمة الفروقات"""
        real_a = self._resolve(dir_a)
        real_b = self._resolve(dir_b)

        for p, label in [(real_a, 'A'), (real_b, 'B')]:
            if not os.path.isdir(p):
                return {"success": False, "error": f"المجلد {label} غير موجود: {p}"}

        comparison = filecmp.dircmp(real_a, real_b)

        result = {
            "success": True,
            "dir_a": real_a,
            "dir_b": real_b,
            "only_in_a": comparison.left_only,
            "only_in_b": comparison.right_only,
            "different_files": comparison.diff_files,
            "identical_files": comparison.same_files,
            "summary": {
                "only_in_a": len(comparison.left_only),
                "only_in_b": len(comparison.right_only),
                "different": len(comparison.diff_files),
                "identical": len(comparison.same_files)
            }
        }
        return result

    def sync_dirs(self, src: str, dst: str,
                  direction: str = 'a_to_b',
                  delete_extra: bool = False) -> dict:
        """
        يُزامن مجلدين.
        direction: 'a_to_b' | 'b_to_a'
        delete_extra: إذا True يحذف من الوجهة ما ليس في المصدر
        """
        real_src = self._resolve(src if direction == 'a_to_b' else dst)
        real_dst = self._resolve(dst if direction == 'a_to_b' else src)

        if not os.path.isdir(real_src):
            return {"success": False, "error": f"المصدر غير موجود: {real_src}"}

        copied = []
        deleted = []
        errors = []

        for root, dirs, files in os.walk(real_src):
            dirs[:] = [d for d in dirs if d not in {'.git', 'venv', '__pycache__'}]
            rel = os.path.relpath(root, real_src)
            dst_dir = os.path.join(real_dst, rel)
            os.makedirs(dst_dir, exist_ok=True)

            for fname in files:
                src_file = os.path.join(root, fname)
                dst_file = os.path.join(dst_dir, fname)
                try:
                    if not os.path.exists(dst_file) or \
                       os.path.getmtime(src_file) > os.path.getmtime(dst_file):
                        shutil.copy2(src_file, dst_file)
                        copied.append(os.path.relpath(dst_file, real_dst))
                except Exception as e:
                    errors.append(f"{fname}: {str(e)}")

        if delete_extra:
            for root, dirs, files in os.walk(real_dst):
                rel = os.path.relpath(root, real_dst)
                src_dir = os.path.join(real_src, rel)
                for fname in files:
                    if not os.path.exists(os.path.join(src_dir, fname)):
                        try:
                            os.remove(os.path.join(root, fname))
                            deleted.append(fname)
                        except Exception as e:
                            errors.append(f"حذف {fname}: {str(e)}")

        return {
            "success": len(errors) == 0,
            "copied_files": len(copied),
            "deleted_files": len(deleted),
            "errors": errors,
            "copied_preview": copied[:10],
            "deleted_preview": deleted[:10]
        }

    def _resolve(self, path: str) -> str:
        if os.path.isabs(path):
            return os.path.normpath(path)
        return os.path.normpath(os.path.join(self.base, path))


fs_diff = FSDiff()
