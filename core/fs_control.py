"""
core/fs_control.py
وحدة التحكم الكاملة بالملفات — مستوحاة من COWORK
تقرأ، تعدّل، تنظّم، تنقل، ترتّب، تحذف مع تحقق كامل
"""
import os
import shutil
import stat
import zipfile
import tarfile
import hashlib
import difflib
from datetime import datetime
from typing import Optional, List, Dict, Tuple
from pathlib import Path
from core.env_config import BASE_DIR, WORKSPACE_DIR, PROJECT_ROOT


# ─── ثوابت الملفات النصية القابلة للقراءة ───
TEXT_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss',
    '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
    '.md', '.txt', '.rst', '.sh', '.bash', '.env', '.env.example',
    '.sql', '.xml', '.csv', '.log', '.gitignore', '.dockerfile',
    'Dockerfile', 'Makefile', 'requirements.txt', 'package.json'
}

# ─── الملفات/المجلدات المحمية التي لا يُمسّها NEXUM ───
PROTECTED_PATHS = {
    '/etc', '/usr', '/bin', '/sbin', '/boot', '/dev', '/proc', '/sys',
    '/root/.ssh', '/etc/passwd', '/etc/shadow'
}


class FileSystemControl:
    """
    التحكم الكامل بالملفات مثل COWORK.
    كل دالة تُعيد dict موحد: {success, data/error, meta}
    """

    def __init__(self):
        self.base = BASE_DIR
        self.workspace = WORKSPACE_DIR

    # ═══════════════════════════════════════════
    # ── قسم القراءة ──
    # ═══════════════════════════════════════════

    def read_file(self, path: str,
                  start_line: int = None,
                  end_line: int = None,
                  encoding: str = 'utf-8') -> dict:
        """
        يقرأ ملفاً كاملاً أو جزءاً منه.
        start_line/end_line: للقراءة الجزئية (1-indexed).
        يُعيد المحتوى مع metadata كاملة.
        """
        real = self._resolve(path)
        if not self._safe(real):
            return self._err(f"المسار محمي: {real}")
        if not os.path.exists(real):
            return self._err(f"لا يوجد ملف: {real}")
        if os.path.isdir(real):
            return self._err(f"هذا مجلد وليس ملفاً: {real}")

        # حجم الملف
        size = os.path.getsize(real)

        # ملفات ثنائية — لا تُقرأ كنص
        if not self._is_text(real) and size > 0:
            return self._ok({
                "type": "binary",
                "path": real,
                "size_kb": round(size / 1024, 2),
                "extension": Path(real).suffix,
                "content": None,
                "note": "ملف ثنائي — لا يمكن قراءته كنص"
            })

        try:
            with open(real, 'r', encoding=encoding, errors='replace') as f:
                lines = f.readlines()

            total_lines = len(lines)

            # قراءة جزئية
            if start_line or end_line:
                s = max(0, (start_line or 1) - 1)
                e = min(total_lines, end_line or total_lines)
                selected = lines[s:e]
                content = "".join(selected)
                note = f"السطور {s+1}–{e} من أصل {total_lines}"
            else:
                content = "".join(lines)
                note = f"الملف كاملاً ({total_lines} سطر)"

            return self._ok({
                "type": "text",
                "path": real,
                "relative": os.path.relpath(real, self.base),
                "content": content,
                "total_lines": total_lines,
                "size_kb": round(size / 1024, 2),
                "encoding": encoding,
                "extension": Path(real).suffix,
                "modified": datetime.fromtimestamp(os.path.getmtime(real)).strftime("%Y-%m-%d %H:%M:%S"),
                "note": note
            })
        except Exception as e:
            return self._err(str(e))

    def read_lines(self, path: str, line_numbers: List[int]) -> dict:
        """يقرأ سطوراً محددة بالأرقام من ملف"""
        result = self.read_file(path)
        if not result['success']:
            return result

        all_lines = result['data']['content'].splitlines(keepends=True)
        selected = {}
        for n in line_numbers:
            if 1 <= n <= len(all_lines):
                selected[n] = all_lines[n - 1].rstrip('\n')
            else:
                selected[n] = None  # سطر خارج النطاق
        return self._ok({"lines": selected, "path": path, "total": len(all_lines)})

    def head(self, path: str, n: int = 20) -> dict:
        """يقرأ أول n سطر"""
        return self.read_file(path, start_line=1, end_line=n)

    def tail(self, path: str, n: int = 20) -> dict:
        """يقرأ آخر n سطر"""
        result = self.read_file(path)
        if not result['success']:
            return result
        total = result['data']['total_lines']
        return self.read_file(path, start_line=max(1, total - n + 1), end_line=total)

    # ═══════════════════════════════════════════
    # ── قسم الكتابة والتعديل ──
    # ═══════════════════════════════════════════

    def write_file(self, path: str, content: str, backup: bool = True) -> dict:
        """
        يكتب ملفاً جديداً أو يستبدل موجوداً.
        backup=True: يحفظ نسخة .bak قبل الاستبدال.
        يتحقق فوراً بعد الكتابة.
        """
        real = self._resolve(path)
        if not self._safe(real):
            return self._err(f"المسار محمي: {real}")

        os.makedirs(os.path.dirname(real), exist_ok=True)
        backup_path = None

        if backup and os.path.exists(real):
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = real + f".bak.{ts}"
            shutil.copy2(real, backup_path)

        try:
            with open(real, 'w', encoding='utf-8') as f:
                f.write(content)
            # تحقق فوري
            with open(real, 'r', encoding='utf-8') as f:
                written = f.read()
            if written != content:
                return self._err("فشل التحقق: المحتوى المكتوب لا يطابق المطلوب")

            return self._ok({
                "path": real,
                "relative": os.path.relpath(real, self.base),
                "lines": len(content.splitlines()),
                "size_kb": round(os.path.getsize(real) / 1024, 2),
                "backup": backup_path,
                "action": "overwritten" if backup_path else "created"
            })
        except Exception as e:
            return self._err(str(e))

    def insert_lines(self, path: str, after_line: int, new_content: str) -> dict:
        """
        يُدرج نصاً بعد سطر محدد.
        after_line=0: يُدرج في بداية الملف.
        after_line=-1: يُضيف في نهاية الملف.
        """
        result = self.read_file(path)
        if not result['success']:
            return result

        lines = result['data']['content'].splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        # ضمان newline في آخر كل سطر جديد
        new_lines = [l if l.endswith('\n') else l + '\n' for l in new_lines]

        if after_line == -1:
            lines.extend(new_lines)
        elif after_line == 0:
            lines = new_lines + lines
        else:
            pos = min(after_line, len(lines))
            lines = lines[:pos] + new_lines + lines[pos:]

        new_content_full = "".join(lines)
        write_result = self.write_file(path, new_content_full)
        if write_result['success']:
            write_result['data']['inserted_lines'] = len(new_lines)
            write_result['data']['inserted_after'] = after_line
        return write_result

    def delete_lines(self, path: str, start_line: int, end_line: int) -> dict:
        """يحذف سطوراً من start_line إلى end_line (شامل)"""
        result = self.read_file(path)
        if not result['success']:
            return result

        lines = result['data']['content'].splitlines(keepends=True)
        total = len(lines)

        if start_line < 1 or end_line > total or start_line > end_line:
            return self._err(f"نطاق سطور غير صالح: {start_line}–{end_line} (الملف {total} سطر)")

        deleted = lines[start_line - 1:end_line]
        remaining = lines[:start_line - 1] + lines[end_line:]

        write_result = self.write_file(path, "".join(remaining))
        if write_result['success']:
            write_result['data']['deleted_lines_count'] = len(deleted)
            write_result['data']['deleted_preview'] = "".join(deleted[:3])
        return write_result

    def replace_text(self, path: str, old_text: str, new_text: str,
                     all_occurrences: bool = False) -> dict:
        """
        يستبدل نصاً في ملف.
        يتحقق من وجود النص القديم.
        يُعيد diff واضحاً.
        """
        result = self.read_file(path)
        if not result['success']:
            return result

        original = result['data']['content']
        count = original.count(old_text)

        if count == 0:
            return self._err(
                f"النص غير موجود في الملف.\n"
                f"힌트: تأكد من المسافات وحروف الإسالة"
            )

        if not all_occurrences and count > 1:
            return self._err(
                f"النص موجود {count} مرات. استخدم all_occurrences=True لاستبدال الكل "
                f"أو حدّد النص بشكل أدق."
            )

        if all_occurrences:
            new_content = original.replace(old_text, new_text)
            replaced = count
        else:
            new_content = original.replace(old_text, new_text, 1)
            replaced = 1

        # توليد diff مختصر
        diff_lines = list(difflib.unified_diff(
            original.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=f"{path} (قبل)",
            tofile=f"{path} (بعد)",
            n=2
        ))
        diff_preview = "".join(diff_lines[:25])

        write_result = self.write_file(path, new_content)
        if write_result['success']:
            write_result['data']['replaced_count'] = replaced
            write_result['data']['diff_preview'] = diff_preview
        return write_result

    def append_to_file(self, path: str, content: str) -> dict:
        """يُضيف نصاً في نهاية ملف موجود"""
        real = self._resolve(path)
        if not self._safe(real):
            return self._err(f"المسار محمي: {real}")
        if not os.path.exists(real):
            return self.write_file(path, content)  # ينشئه إذا لم يكن موجوداً
        try:
            original_lines = open(real, 'r', encoding='utf-8').readlines()
            with open(real, 'a', encoding='utf-8') as f:
                if not content.startswith('\n') and original_lines and not original_lines[-1].endswith('\n'):
                    f.write('\n')
                f.write(content)
            new_lines = open(real, 'r', encoding='utf-8').readlines()
            return self._ok({
                "path": real,
                "appended_lines": len(new_lines) - len(original_lines),
                "total_lines": len(new_lines)
            })
        except Exception as e:
            return self._err(str(e))

    # ═══════════════════════════════════════════
    # ── قسم التنظيم والنقل ──
    # ═══════════════════════════════════════════

    def move(self, src: str, dst: str, overwrite: bool = False) -> dict:
        """ينقل ملفاً أو مجلداً"""
        real_src = self._resolve(src)
        real_dst = self._resolve(dst)

        for p in [real_src, real_dst]:
            if not self._safe(p):
                return self._err(f"المسار محمي: {p}")

        if not os.path.exists(real_src):
            return self._err(f"المصدر غير موجود: {real_src}")

        if os.path.exists(real_dst) and not overwrite:
            return self._err(
                f"الوجهة موجودة مسبقاً: {real_dst}\n"
                f"استخدم overwrite=True للاستبدال."
            )

        try:
            os.makedirs(os.path.dirname(real_dst), exist_ok=True)
            shutil.move(real_src, real_dst)
            return self._ok({
                "moved_from": real_src,
                "moved_to": real_dst,
                "exists_at_destination": os.path.exists(real_dst),
                "exists_at_source": os.path.exists(real_src)
            })
        except Exception as e:
            return self._err(str(e))

    def copy(self, src: str, dst: str, overwrite: bool = False) -> dict:
        """ينسخ ملفاً أو مجلداً"""
        real_src = self._resolve(src)
        real_dst = self._resolve(dst)

        for p in [real_src, real_dst]:
            if not self._safe(p):
                return self._err(f"المسار محمي: {p}")

        if not os.path.exists(real_src):
            return self._err(f"المصدر غير موجود: {real_src}")

        if os.path.exists(real_dst) and not overwrite:
            return self._err(f"الوجهة موجودة: {real_dst}")

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
                "copied_from": real_src,
                "copied_to": real_dst,
                "size_kb": round(size / 1024, 2)
            })
        except Exception as e:
            return self._err(str(e))

    def rename(self, path: str, new_name: str) -> dict:
        """يُعيد تسمية ملف أو مجلد (الاسم فقط، ليس المسار)"""
        real = self._resolve(path)
        if not self._safe(real):
            return self._err(f"المسار محمي: {real}")
        if not os.path.exists(real):
            return self._err(f"غير موجود: {real}")

        parent = os.path.dirname(real)
        new_path = os.path.join(parent, new_name)

        if os.path.exists(new_path):
            return self._err(f"الاسم الجديد مستخدم مسبقاً: {new_path}")

        try:
            os.rename(real, new_path)
            return self._ok({
                "old_path": real,
                "new_path": new_path,
                "old_name": os.path.basename(real),
                "new_name": new_name
            })
        except Exception as e:
            return self._err(str(e))

    def delete(self, path: str, force: bool = False) -> dict:
        """
        يحذف ملفاً أو مجلداً.
        force=False: يتطلب تأكيداً للمجلدات.
        """
        real = self._resolve(path)
        if not self._safe(real):
            return self._err(f"المسار محمي — لا يمكن الحذف: {real}")
        if not os.path.exists(real):
            return self._err(f"غير موجود: {real}")

        is_dir = os.path.isdir(real)

        if is_dir and not force:
            count = sum(len(files) for _, _, files in os.walk(real))
            return {
                "success": False,
                "status": "confirm_required",
                "error": f"المجلد يحتوي على {count} ملف. استخدم force=True للتأكيد.",
                "path": real,
                "file_count": count
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
            return self._err(str(e))

    def create_dir(self, path: str) -> dict:
        """ينشئ مجلداً (مع كل المجلدات الأب)"""
        real = self._resolve(path)
        if not self._safe(real):
            return self._err(f"المسار محمي: {real}")
        existed = os.path.exists(real)
        try:
            os.makedirs(real, exist_ok=True)
            return self._ok({
                "path": real,
                "created": not existed,
                "already_existed": existed
            })
        except Exception as e:
            return self._err(str(e))

    def get_permissions(self, path: str) -> dict:
        """يعرض صلاحيات ملف"""
        real = self._resolve(path)
        if not os.path.exists(real):
            return self._err(f"غير موجود: {real}")
        st = os.stat(real)
        mode = oct(st.st_mode)[-3:]
        readable = os.access(real, os.R_OK)
        writable = os.access(real, os.W_OK)
        executable = os.access(real, os.X_OK)
        return self._ok({
            "path": real,
            "octal": mode,
            "readable": readable,
            "writable": writable,
            "executable": executable
        })

    def chmod(self, path: str, mode: int) -> dict:
        """يُغيّر صلاحيات ملف (مثال: mode=755)"""
        real = self._resolve(path)
        if not self._safe(real):
            return self._err(f"المسار محمي: {real}")
        if not os.path.exists(real):
            return self._err(f"غير موجود: {real}")
        try:
            os.chmod(real, int(str(mode), 8))
            return self._ok({"path": real, "new_mode": mode})
        except Exception as e:
            return self._err(str(e))

    # ═══════════════════════════════════════════
    # ── قسم الضغط والفك ──
    # ═══════════════════════════════════════════

    def compress(self, path: str, output_name: str = None,
                 format: str = 'zip') -> dict:
        """يضغط ملفاً أو مجلداً"""
        real = self._resolve(path)
        if not os.path.exists(real):
            return self._err(f"غير موجود: {real}")

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
                return self._err(f"تنسيق غير مدعوم: {format}. المتاح: zip, tar.gz")

            return self._ok({
                "compressed": real,
                "output": out_path,
                "size_kb": round(os.path.getsize(out_path) / 1024, 2),
                "format": format
            })
        except Exception as e:
            return self._err(str(e))

    def extract(self, archive_path: str, destination: str = None) -> dict:
        """يفكّ ضغط ملف"""
        real = self._resolve(archive_path)
        if not os.path.exists(real):
            return self._err(f"الأرشيف غير موجود: {real}")

        dest = self._resolve(destination) if destination else os.path.dirname(real)
        os.makedirs(dest, exist_ok=True)

        try:
            if zipfile.is_zipfile(real):
                with zipfile.ZipFile(real, 'r') as zf:
                    zf.extractall(dest)
                    names = zf.namelist()
            elif tarfile.is_tarfile(real):
                with tarfile.open(real, 'r:*') as tf:
                    tf.extractall(dest)
                    names = tf.getnames()
            else:
                return self._err(f"تنسيق أرشيف غير معروف: {real}")

            return self._ok({
                "extracted_to": dest,
                "files_count": len(names),
                "files_preview": names[:5]
            })
        except Exception as e:
            return self._err(str(e))

    # ═══════════════════════════════════════════
    # ── قسم hash وسلامة الملفات ──
    # ═══════════════════════════════════════════

    def get_hash(self, path: str, algorithm: str = 'sha256') -> dict:
        """يحسب hash ملف للتحقق من سلامته"""
        real = self._resolve(path)
        if not os.path.exists(real):
            return self._err(f"غير موجود: {real}")
        try:
            h = hashlib.new(algorithm)
            with open(real, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    h.update(chunk)
            return self._ok({"path": real, "algorithm": algorithm, "hash": h.hexdigest()})
        except Exception as e:
            return self._err(str(e))

    # ═══════════════════════════════════════════
    # ── دوال مساعدة داخلية ──
    # ═══════════════════════════════════════════

    def _resolve(self, path: str) -> str:
        """يحوّل المسار لمسار حقيقي مطلق"""
        if os.path.isabs(path):
            return os.path.normpath(path)
        # إذا بدأ بـ workspace يوضع فيه
        if path.startswith('workspace/') or path.startswith('workspace\\'):
            return os.path.normpath(os.path.join(self.workspace, path[10:]))
        # غير ذلك في جذر المشروع
        return os.path.normpath(os.path.join(self.base, path))

    def _safe(self, path: str) -> bool:
        """يتحقق أن المسار ليس محمياً"""
        return not any(path.startswith(p) for p in PROTECTED_PATHS)

    def _is_text(self, path: str) -> bool:
        """يتحقق إذا كان الملف نصياً"""
        ext = Path(path).suffix.lower()
        name = os.path.basename(path)
        return ext in TEXT_EXTENSIONS or name in TEXT_EXTENSIONS

    def _dir_size(self, path: str) -> int:
        """يحسب الحجم الكلي لمجلد"""
        total = 0
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                try:
                    total += os.path.getsize(os.path.join(dirpath, f))
                except Exception:
                    pass
        return total

    def _ok(self, data: dict) -> dict:
        return {"success": True, "data": data}

    def _err(self, message: str) -> dict:
        return {"success": False, "error": message, "data": None}


fs_control = FileSystemControl()
