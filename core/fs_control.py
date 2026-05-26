# -*- coding: utf-8 -*-
"""
core/fs_control.py
وحدة التحكم الكاملة بالملفات والمسارات -- النسخة المحصنة سياديا بالكامل (v7.2.5)
================================================================================
- معالجة جراحية لثغرات الـ Zip Slip و Tar Slip باستخدام os.path.commonpath الآمن.
- فرض جدار حماية (Sovereign Jailbreak Sandbox) يمنع التعديل على النواة والوكلاء افتراضيا.
- فحص تقديري لحجم المجلدات قبل الضغط لمنع تجميد المعالج (Anti-CPU Exhaustion).
"""

import os
import sys
import shutil
import stat
import zipfile
import tarfile
import hashlib
import difflib
import tempfile
from datetime import datetime
from typing import Optional, List, Dict, Tuple
from pathlib import Path

# استيراد الاعتماديات الأساسية بشكل معزول وآمن
try:
    from core.env_config import BASE_DIR, WORKSPACE_DIR, PROJECT_ROOT
except ImportError:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    WORKSPACE_DIR = os.path.join(BASE_DIR, "workspace")
    PROJECT_ROOT = BASE_DIR

# ─── ثوابت الملفات النصية المسموح بقراءتها ومعالجتها ───
TEXT_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss',
    '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
    '.md', '.txt', '.rst', '.sh', '.bash', '.env', '.env.example',
    '.sql', '.xml', '.csv', '.log', '.gitignore', '.dockerfile',
    'Dockerfile', 'Makefile', 'requirements.txt', 'package.json'
}

# ─── الملفات والمجلدات المحمية (Linux + Windows) ───
if sys.platform == "win32":
    _sysroot = os.environ.get("SYSTEMROOT", r"C:\Windows")
    PROTECTED_PATHS = {
        _sysroot,
        os.path.join(_sysroot, "System32"),
        os.path.join(os.environ.get("PROGRAMFILES", r"C:\Program Files")),
    }
else:
    PROTECTED_PATHS = {
        '/etc', '/usr', '/bin', '/sbin', '/boot', '/dev', '/proc', '/sys',
        '/root/.ssh', '/etc/passwd', '/etc/shadow', '/var/run', '/var/log'
    }

# مجلد الملفات المؤقتة (متوافق مع كل الأنظمة)
SYSTEM_TEMP = tempfile.gettempdir()


class FileSystemControl:
    """
    متحكم نظام الملفات السيادي المعزول والمحصن.
    جميع الدوال تعيد قوالب بيانات موحدة:
    { "success": bool, "data": dict, "error": Optional[str] }
    """

    def __init__(self, allow_core_edit: bool = False):
        self.base = os.path.realpath(BASE_DIR)
        self.workspace = os.path.realpath(WORKSPACE_DIR)
        self.allow_core_edit = allow_core_edit
        os.makedirs(self.workspace, exist_ok=True)

    # ===============================================
    # -- قسم القراءة والاستعلام الآمن --
    # ===============================================

    def read_file(self, path: str, start_line: int = None,
                  end_line: int = None, encoding: str = 'utf-8') -> dict:
        """يقرأ ملفا بالكامل أو جزءا محددا منه مع فحص أمني للمسار الحقيقي."""
        real = self._resolve(path)
        if not self._safe(real):
            return self._err(f"Access Denied: path outside sovereign boundaries: {real}")
        if not os.path.exists(real):
            return self._err(f"File not found: {real}")
        if os.path.isdir(real):
            return self._err(f"Path is a directory, not a file: {real}")

        size = os.path.getsize(real)

        if not self._is_text(real) and size > 0:
            return self._ok({
                "type": "binary", "path": real,
                "size_kb": round(size / 1024, 2),
                "extension": Path(real).suffix,
                "content": None,
                "note": "Binary file - not readable as text"
            })

        try:
            with open(real, 'r', encoding=encoding, errors='replace') as f:
                lines = f.readlines()

            total_lines = len(lines)

            if start_line or end_line:
                s = max(0, (start_line or 1) - 1)
                e = min(total_lines, end_line or total_lines)
                selected = lines[s:e]
                content = "".join(selected)
                note = f"Read lines {s+1} to {e} of {total_lines} total."
            else:
                content = "".join(lines)
                note = f"Read complete file ({total_lines} lines)"

            return self._ok({
                "type": "text", "path": real,
                "relative": os.path.relpath(real, self.base),
                "content": content, "total_lines": total_lines,
                "size_kb": round(size / 1024, 2),
                "encoding": encoding,
                "extension": Path(real).suffix,
                "modified": datetime.fromtimestamp(os.path.getmtime(real)).strftime("%Y-%m-%d %H:%M:%S"),
                "note": note
            })
        except Exception as e:
            return self._err(f"Read failed: {str(e)}")

    def read_lines(self, path: str, line_numbers: List[int]) -> dict:
        """يقرأ أسطر محددة من الملف بناء على قائمة الأرقام الممررة."""
        result = self.read_file(path)
        if not result['success']:
            return result
        all_lines = result['data']['content'].splitlines(keepends=True)
        selected = {}
        for n in line_numbers:
            if 1 <= n <= len(all_lines):
                selected[n] = all_lines[n - 1].rstrip('\n')
            else:
                selected[n] = None
        return self._ok({"lines": selected, "path": path, "total": len(all_lines)})

    def head(self, path: str, n: int = 20) -> dict:
        """قراءة أول n سطر من الملف."""
        return self.read_file(path, start_line=1, end_line=n)

    def tail(self, path: str, n: int = 20) -> dict:
        """قراءة آخر n سطر من الملف."""
        result = self.read_file(path)
        if not result['success']:
            return result
        total = result['data']['total_lines']
        return self.read_file(path, start_line=max(1, total - n + 1), end_line=total)

    # ===============================================
    # -- قسم الكتابة والتعديل المحمي --
    # ===============================================

    def write_file(self, path: str, content: str, backup: bool = True) -> dict:
        """يكتب ملفا جديدا أو يستبدل موجودا مع نسخة احتياطية .bak وفحص تكامل."""
        real = self._resolve(path)
        if not self._safe(real):
            return self._err(f"Access Denied: write path outside boundaries: {real}")
        if not self.allow_core_edit and self._is_core_file(real):
            return self._err(f"Core file protection: editing locked for stability: {real}")

        os.makedirs(os.path.dirname(real), exist_ok=True)
        backup_path = None

        if backup and os.path.exists(real):
            try:
                ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = real + f".bak.{ts}"
                shutil.copy2(real, backup_path)
            except Exception as e:
                print(f"[Sovereign FS Warning] Backup generation failed: {e}")

        try:
            with open(real, 'w', encoding='utf-8') as f:
                f.write(content)

            # Strict Integrity Check
            with open(real, 'r', encoding='utf-8') as f:
                written_data = f.read()
            if written_data != content:
                return self._err("Integrity check failed: written content mismatch!")

            return self._ok({
                "path": real,
                "relative": os.path.relpath(real, self.base),
                "lines": len(content.splitlines()),
                "size_kb": round(os.path.getsize(real) / 1024, 2),
                "backup": backup_path,
                "action": "overwritten" if backup_path else "created"
            })
        except Exception as e:
            return self._err(f"Write failed: {str(e)}")

    def insert_lines(self, path: str, after_line: int, new_content: str) -> dict:
        """يدرج نصا برمجيا بعد سطر محدد."""
        result = self.read_file(path)
        if not result['success']:
            return result

        lines = result['data']['content'].splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        new_lines = [l if l.endswith('\n') else l + '\n' for l in new_lines]

        if after_line == -1:
            lines.extend(new_lines)
        elif after_line == 0:
            lines = new_lines + lines
        else:
            pos = min(after_line, len(lines))
            lines = lines[:pos] + new_lines + lines[pos:]

        write_result = self.write_file(path, "".join(lines))
        if write_result['success']:
            write_result['data']['inserted_lines'] = len(new_lines)
            write_result['data']['inserted_after'] = after_line
        return write_result

    def delete_lines(self, path: str, start_line: int, end_line: int) -> dict:
        """يحذف أسطرا محددة من الملف البرمجي."""
        result = self.read_file(path)
        if not result['success']:
            return result

        lines = result['data']['content'].splitlines(keepends=True)
        total = len(lines)

        if start_line < 1 or end_line > total or start_line > end_line:
            return self._err(f"Invalid line range: {start_line}-{end_line} (total: {total})")

        deleted = lines[start_line - 1:end_line]
        remaining = lines[:start_line - 1] + lines[end_line:]

        write_result = self.write_file(path, "".join(remaining))
        if write_result['success']:
            write_result['data']['deleted_lines_count'] = len(deleted)
            write_result['data']['deleted_preview'] = "".join(deleted[:3])
        return write_result

    def replace_text(self, path: str, old_text: str, new_text: str,
                     all_occurrences: bool = False) -> dict:
        """يستبدل نصا محددا داخل الملف مع عرض الفروقات."""
        result = self.read_file(path)
        if not result['success']:
            return result

        original = result['data']['content']
        count = original.count(old_text)

        if count == 0:
            return self._err("Target text not found in file.")
        if not all_occurrences and count > 1:
            return self._err(f"Text found {count} times. Use all_occurrences=True or be more specific.")

        if all_occurrences:
            new_content = original.replace(old_text, new_text)
            replaced = count
        else:
            new_content = original.replace(old_text, new_text, 1)
            replaced = 1

        diff_lines = list(difflib.unified_diff(
            original.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=f"{path} (Original)",
            tofile=f"{path} (Modified)", n=2
        ))
        diff_preview = "".join(diff_lines[:25])

        write_result = self.write_file(path, new_content)
        if write_result['success']:
            write_result['data']['replaced_count'] = replaced
            write_result['data']['diff_preview'] = diff_preview
        return write_result

    def append_to_file(self, path: str, content: str) -> dict:
        """يضيف نصا جديدا في نهاية ملف موجود."""
        real = self._resolve(path)
        if not self._safe(real):
            return self._err(f"Access Denied: path protected: {real}")
        if not self.allow_core_edit and self._is_core_file(real):
            return self._err(f"Core file protection: editing locked: {real}")
        if not os.path.exists(real):
            return self.write_file(path, content)

        try:
            with open(real, 'r', encoding='utf-8') as f:
                original_lines = f.readlines()
            with open(real, 'a', encoding='utf-8') as f:
                if not content.startswith('\n') and original_lines and not original_lines[-1].endswith('\n'):
                    f.write('\n')
                f.write(content)
            with open(real, 'r', encoding='utf-8') as f:
                new_lines = f.readlines()
            return self._ok({
                "path": real,
                "appended_lines": len(new_lines) - len(original_lines),
                "total_lines": len(new_lines)
            })
        except Exception as e:
            return self._err(f"Append failed: {str(e)}")

    # ===============================================
    # -- قسم النقل وإعادة الترتيب والحذف --
    # ===============================================

    def move(self, src: str, dst: str, overwrite: bool = False) -> dict:
        """ينقل ملفا أو مجلدا كاملا مع تأمين الوجهات."""
        real_src = self._resolve(src)
        real_dst = self._resolve(dst)

        for p in [real_src, real_dst]:
            if not self._safe(p):
                return self._err(f"Access Denied: path protected: {p}")
            if not self.allow_core_edit and self._is_core_file(p):
                return self._err(f"Core file protection: move blocked: {p}")

        if not os.path.exists(real_src):
            return self._err(f"Source not found: {real_src}")
        if os.path.exists(real_dst) and not overwrite:
            return self._err(f"Destination exists. Use overwrite=True.")

        try:
            os.makedirs(os.path.dirname(real_dst), exist_ok=True)
            shutil.move(real_src, real_dst)
            return self._ok({
                "moved_from": real_src, "moved_to": real_dst,
                "exists_at_destination": os.path.exists(real_dst),
                "exists_at_source": os.path.exists(real_src)
            })
        except Exception as e:
            return self._err(f"Move failed: {str(e)}")

    def copy(self, src: str, dst: str, overwrite: bool = False) -> dict:
        """ينسخ ملفا أو مجلدا برمجيا بالكامل."""
        real_src = self._resolve(src)
        real_dst = self._resolve(dst)

        for p in [real_src, real_dst]:
            if not self._safe(p):
                return self._err(f"Access Denied: path protected: {p}")
        if not self.allow_core_edit and self._is_core_file(real_dst):
            return self._err(f"Core file protection: copy to core blocked: {real_dst}")
        if not os.path.exists(real_src):
            return self._err(f"Source not found: {real_src}")
        if os.path.exists(real_dst) and not overwrite:
            return self._err(f"Destination exists. Use overwrite=True.")

        try:
            os.makedirs(os.path.dirname(real_dst), exist_ok=True)
            if os.path.isdir(real_src):
                if os.path.exists(real_dst) and overwrite:
                    shutil.rmtree(real_dst)
                shutil.copytree(real_src, real_dst)
                size = self._dir_size(real_dst)
            else:
                shutil.copy2(real_src, real_dst)
                size = os.path.getsize(real_dst)
            return self._ok({
                "copied_from": real_src, "copied_to": real_dst,
                "size_kb": round(size / 1024, 2)
            })
        except Exception as e:
            return self._err(f"Copy failed: {str(e)}")

    def rename(self, path: str, new_name: str) -> dict:
        """يغير اسم الملف أو المجلد."""
        real = self._resolve(path)
        if not self._safe(real):
            return self._err(f"Access Denied: path protected: {real}")
        if not self.allow_core_edit and self._is_core_file(real):
            return self._err(f"Core file protection: rename blocked: {real}")
        if not os.path.exists(real):
            return self._err(f"Not found: {real}")

        parent = os.path.dirname(real)
        new_path = os.path.join(parent, new_name)
        if os.path.exists(new_path):
            return self._err(f"Name already in use: {new_path}")

        try:
            os.rename(real, new_path)
            return self._ok({
                "old_path": real, "new_path": new_path,
                "old_name": os.path.basename(real), "new_name": new_name
            })
        except Exception as e:
            return self._err(f"Rename failed: {str(e)}")

    def delete(self, path: str, force: bool = False) -> dict:
        """يحذف ملفا أو مجلدا مع حماية النواة."""
        real = self._resolve(path)
        if not self._safe(real):
            return self._err(f"Access Denied: cannot delete protected resource: {real}")
        if not self.allow_core_edit and self._is_core_file(real):
            return self._err(f"Core file protection: delete blocked: {real}")
        if not os.path.exists(real):
            return self._err(f"Not found: {real}")

        is_dir = os.path.isdir(real)

        if is_dir and not force:
            count = sum(len(files) for _, _, files in os.walk(real))
            return {
                "success": False,
                "status": "confirm_required",
                "error": f"Directory contains {count} files. Use force=True to confirm.",
                "path": real, "file_count": count
            }

        try:
            if is_dir:
                shutil.rmtree(real)
            else:
                os.remove(real)
            return self._ok({
                "deleted": real,
                "type": "directory" if is_dir else "file",
                "exists_after": os.path.exists(real)
            })
        except Exception as e:
            return self._err(f"Delete failed: {str(e)}")

    def create_dir(self, path: str) -> dict:
        """ينشئ مجلدا مع كافة المجلدات الشجرية."""
        real = self._resolve(path)
        if not self._safe(real):
            return self._err(f"Access Denied: path outside boundaries: {real}")
        existed = os.path.exists(real)
        try:
            os.makedirs(real, exist_ok=True)
            return self._ok({"path": real, "created": not existed, "already_existed": existed})
        except Exception as e:
            return self._err(f"Create dir failed: {str(e)}")

    def get_permissions(self, path: str) -> dict:
        """يستعلم عن صلاحيات القراءة والكتابة والتشغيل للمورد."""
        real = self._resolve(path)
        if not os.path.exists(real):
            return self._err(f"Not found: {real}")
        st = os.stat(real)
        mode = oct(st.st_mode)[-3:]
        return self._ok({
            "path": real, "octal": mode,
            "readable": os.access(real, os.R_OK),
            "writable": os.access(real, os.W_OK),
            "executable": os.access(real, os.X_OK)
        })

    def chmod(self, path: str, mode: int) -> dict:
        """يغير صلاحيات الملف (مثال: mode=755)."""
        real = self._resolve(path)
        if not self._safe(real):
            return self._err(f"Access Denied: path protected: {real}")
        if not os.path.exists(real):
            return self._err(f"Not found: {real}")
        try:
            os.chmod(real, int(str(mode), 8))
            return self._ok({"path": real, "new_mode": mode})
        except Exception as e:
            return self._err(f"chmod failed: {str(e)}")

    # ===============================================
    # -- قسم الضغط والأرشفة وفك الملفات --
    # ===============================================

    def compress(self, path: str, output_name: str = None,
                 format: str = 'zip') -> dict:
        """يضغط ملفا أو مجلدا مع فحص حد الحجم (500MB max)."""
        real = self._resolve(path)
        if not os.path.exists(real):
            return self._err(f"Not found: {real}")

        if os.path.isdir(real):
            dir_size_bytes = self._dir_size(real)
            max_allowed_bytes = 500 * 1024 * 1024
            if dir_size_bytes > max_allowed_bytes:
                return self._err(f"Directory too large ({round(dir_size_bytes / (1024*1024), 2)}MB). Max: 500MB.")

        name = output_name or (os.path.basename(real) + f".{format}")
        out_path = os.path.join(os.path.dirname(real), name)

        try:
            if format == 'zip':
                with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                    if os.path.isdir(real):
                        for root, dirs, files in os.walk(real):
                            for file in files:
                                fp = os.path.join(root, file)
                                zf.write(fp, os.path.relpath(fp, os.path.dirname(real)))
                    else:
                        zf.write(real, os.path.basename(real))
            elif format in ('tar.gz', 'tgz'):
                with tarfile.open(out_path, 'w:gz') as tf:
                    tf.add(real, arcname=os.path.basename(real))
            else:
                return self._err(f"Unsupported format: {format}. Use: zip, tar.gz")

            return self._ok({
                "compressed": real, "output": out_path,
                "size_kb": round(os.path.getsize(out_path) / 1024, 2),
                "format": format
            })
        except Exception as e:
            return self._err(f"Compress failed: {str(e)}")

    def extract(self, archive_path: str, destination: str = None) -> dict:
        """يفك الضغط مع حماية ضد Zip Slip و Tar Slip."""
        real = self._resolve(archive_path)
        if not os.path.exists(real):
            return self._err(f"Archive not found: {real}")

        dest = self._resolve(destination) if destination else os.path.dirname(real)
        os.makedirs(dest, exist_ok=True)
        dest_realpath = os.path.realpath(dest)

        try:
            if zipfile.is_zipfile(real):
                with zipfile.ZipFile(real, 'r') as zf:
                    for member in zf.namelist():
                        target_path = os.path.join(dest, member)
                        if not self._is_safe_extraction(dest_realpath, target_path):
                            return self._err(f"Zip Slip detected: {member}")
                    zf.extractall(dest_realpath)
                    names = zf.namelist()
            elif tarfile.is_tarfile(real):
                with tarfile.open(real, 'r:*') as tf:
                    for member in tf.getmembers():
                        target_path = os.path.join(dest, member.name)
                        if not self._is_safe_extraction(dest_realpath, target_path):
                            return self._err(f"Tar Slip detected: {member.name}")
                    tf.extractall(dest_realpath)
                    names = tf.getnames()
            else:
                return self._err(f"Unsupported archive format: {real}")

            return self._ok({
                "extracted_to": dest_realpath,
                "files_count": len(names),
                "files_preview": names[:5]
            })
        except Exception as e:
            return self._err(f"Extract failed: {str(e)}")

    # ===============================================
    # -- قسم التحقق والتكامل --
    # ===============================================

    def get_hash(self, path: str, algorithm: str = 'sha256') -> dict:
        """يحسب بصمة Hash الخاصة بالملف."""
        real = self._resolve(path)
        if not os.path.exists(real):
            return self._err(f"Not found: {real}")
        try:
            h = hashlib.new(algorithm)
            with open(real, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    h.update(chunk)
            return self._ok({"path": real, "algorithm": algorithm, "hash": h.hexdigest()})
        except Exception as e:
            return self._err(f"Hash computation failed: {str(e)}")

    # ===============================================
    # -- دوال الأمان الداخلية --
    # ===============================================

    def _resolve(self, path: str) -> str:
        """يحل المسارات إلى مسار فيزيائي حقيقي مع فك Symbolic Links."""
        path_str = str(path)
        if os.path.isabs(path_str):
            resolved = os.path.realpath(path_str)
        elif path_str.startswith('workspace/') or path_str.startswith('workspace\\'):
            resolved = os.path.realpath(os.path.join(self.workspace, path_str[10:]))
        else:
            resolved = os.path.realpath(os.path.join(self.base, path_str))
        return resolved

    def _safe(self, path: str) -> bool:
        """يتحقق أن المسار آمن ومعزول داخل حدود المشروع."""
        resolved_path = os.path.realpath(path)
        if any(resolved_path.startswith(os.path.realpath(p)) for p in PROTECTED_PATHS):
            return False
        is_in_base = resolved_path.startswith(self.base)
        is_in_workspace = resolved_path.startswith(self.workspace)
        is_in_temp = resolved_path.startswith(SYSTEM_TEMP)
        return is_in_base or is_in_workspace or is_in_temp

    def _is_safe_extraction(self, dest_dir: str, target: str) -> bool:
        """تحقق Anti-Zip/Tar Slip باستخدام commonpath."""
        dest_realpath = os.path.realpath(dest_dir)
        target_realpath = os.path.realpath(target)
        try:
            common = os.path.commonpath([dest_realpath, target_realpath])
            return common == dest_realpath
        except ValueError:
            return False

    def _is_core_file(self, real_path: str) -> bool:
        """تحدد ما إذا كان المسار يخص ملفات النواة الحساسة."""
        resolved_path = os.path.realpath(real_path)
        rel_to_base = os.path.relpath(resolved_path, self.base)
        if rel_to_base.startswith(".."):
            return False
        parts = rel_to_base.split(os.sep)
        if not parts:
            return False
        if parts[0] == "main.py":
            return True
        if parts[0] in ["core", "agents", "services"]:
            return True
        return False

    def _is_text(self, path: str) -> bool:
        """تحديد نوع الملف نصيا."""
        ext = Path(path).suffix.lower()
        name = os.path.basename(path)
        return ext in TEXT_EXTENSIONS or name in TEXT_EXTENSIONS

    def _dir_size(self, path: str) -> int:
        """حساب الحجم الإجمالي للمجلد بالبايت."""
        total = 0
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                try:
                    total += os.path.getsize(os.path.join(dirpath, f))
                except Exception:
                    pass
        return total

    def _ok(self, data: dict) -> dict:
        return {"success": True, "data": data, "error": None}

    def _err(self, message: str) -> dict:
        return {"success": False, "error": message, "data": None}


fs_control = FileSystemControl()
