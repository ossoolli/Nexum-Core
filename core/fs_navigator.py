"""
core/fs_navigator.py
التنقل والتصفح الهرمي — يرى NEXUM بنية المشروع كاملة
"""
import os
import stat
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from core.env_config import BASE_DIR, WORKSPACE_DIR
from core.fs_control import TEXT_EXTENSIONS, PROTECTED_PATHS


class FSNavigator:
    def __init__(self):
        self.base = BASE_DIR
        self.cwd = BASE_DIR  # المجلد الحالي (يتغير بأمر cd)

    def ls(self, path: str = None, show_hidden: bool = False,
           sort_by: str = 'name') -> dict:
        """
        يعرض محتويات مجلد.
        sort_by: 'name' | 'size' | 'modified' | 'type'
        """
        target = self._resolve(path or self.cwd)
        if not os.path.exists(target):
            return {"success": False, "error": f"المجلد غير موجود: {target}"}
        if not os.path.isdir(target):
            return {"success": False, "error": f"هذا ملف وليس مجلداً"}

        entries = []
        try:
            for name in os.listdir(target):
                if not show_hidden and name.startswith('.'):
                    continue
                full = os.path.join(target, name)
                try:
                    st = os.stat(full)
                    is_dir = os.path.isdir(full)
                    entry = {
                        "name": name,
                        "type": "dir" if is_dir else "file",
                        "size_kb": 0 if is_dir else round(st.st_size / 1024, 2),
                        "modified": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M"),
                        "permissions": oct(st.st_mode)[-3:],
                        "extension": Path(name).suffix if not is_dir else None,
                        "readable": os.access(full, os.R_OK),
                        "writable": os.access(full, os.W_OK),
                    }
                    # عدد عناصر المجلد
                    if is_dir:
                        try:
                            entry["children_count"] = len(os.listdir(full))
                        except PermissionError:
                            entry["children_count"] = "?"
                    entries.append(entry)
                except Exception:
                    pass
        except PermissionError:
            return {"success": False, "error": f"لا توجد صلاحية للوصول: {target}"}

        # الترتيب
        sort_key = {
            'name': lambda x: (x['type'] == 'file', x['name'].lower()),
            'size': lambda x: x['size_kb'],
            'modified': lambda x: x['modified'],
            'type': lambda x: x['type']
        }.get(sort_by, lambda x: x['name'].lower())

        entries.sort(key=sort_key)

        dirs = [e for e in entries if e['type'] == 'dir']
        files = [e for e in entries if e['type'] == 'file']

        return {
            "success": True,
            "path": target,
            "relative": os.path.relpath(target, self.base),
            "dirs": dirs,
            "files": files,
            "total_dirs": len(dirs),
            "total_files": len(files)
        }

    def tree(self, path: str = None, max_depth: int = 3,
             show_hidden: bool = False, max_files: int = 200) -> dict:
        """
        يعرض بنية المجلد بشكل هرمي (مثل أمر tree).
        max_depth: أقصى عمق للتنقل.
        """
        target = self._resolve(path or self.cwd)
        if not os.path.exists(target):
            return {"success": False, "error": f"غير موجود: {target}"}

        lines = []
        file_count = [0]
        dir_count = [0]

        def _walk(current, prefix, depth):
            if depth > max_depth or file_count[0] > max_files:
                return
            try:
                items = sorted(os.listdir(current))
            except PermissionError:
                lines.append(f"{prefix}├── [permission denied]")
                return

            if not show_hidden:
                items = [i for i in items if not i.startswith('.')]

            for i, name in enumerate(items):
                full = os.path.join(current, name)
                connector = "└── " if i == len(items) - 1 else "├── "
                extension = "│   " if i < len(items) - 1 else "    "
                is_dir = os.path.isdir(full)

                if is_dir:
                    dir_count[0] += 1
                    lines.append(f"{prefix}{connector}📁 {name}/")
                    _walk(full, prefix + extension, depth + 1)
                else:
                    file_count[0] += 1
                    size = os.path.getsize(full)
                    size_str = f"{size//1024}KB" if size > 1024 else f"{size}B"
                    lines.append(f"{prefix}{connector}📄 {name} ({size_str})")

        root_name = os.path.basename(target)
        lines.append(f"📁 {root_name}/")
        _walk(target, "", 1)

        if file_count[0] > max_files:
            lines.append(f"... (اقتُصر على {max_files} ملف)")

        return {
            "success": True,
            "path": target,
            "tree": "\n".join(lines),
            "total_files": file_count[0],
            "total_dirs": dir_count[0]
        }

    def cd(self, path: str) -> dict:
        """يغيّر المجلد الحالي"""
        target = self._resolve(path)
        if not os.path.exists(target):
            return {"success": False, "error": f"المجلد غير موجود: {target}"}
        if not os.path.isdir(target):
            return {"success": False, "error": "ليس مجلداً"}
        self.cwd = target
        return {"success": True, "cwd": self.cwd, "relative": os.path.relpath(self.cwd, self.base)}

    def pwd(self) -> dict:
        """يعرض المجلد الحالي"""
        return {
            "success": True,
            "absolute": self.cwd,
            "relative": os.path.relpath(self.cwd, self.base)
        }

    def stat(self, path: str) -> dict:
        """يعرض معلومات تفصيلية عن ملف أو مجلد"""
        target = self._resolve(path)
        if not os.path.exists(target):
            return {"success": False, "error": f"غير موجود: {target}"}

        st = os.stat(target)
        is_dir = os.path.isdir(target)

        info = {
            "name": os.path.basename(target),
            "path": target,
            "type": "directory" if is_dir else "file",
            "size_bytes": st.st_size,
            "size_kb": round(st.st_size / 1024, 2),
            "created": datetime.fromtimestamp(st.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
            "modified": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "permissions_octal": oct(st.st_mode)[-3:],
            "readable": os.access(target, os.R_OK),
            "writable": os.access(target, os.W_OK),
            "executable": os.access(target, os.X_OK),
        }

        if is_dir:
            info["total_size_kb"] = round(
                sum(os.path.getsize(os.path.join(r, f))
                    for r, _, fs in os.walk(target) for f in fs
                    if os.path.exists(os.path.join(r, f))) / 1024, 2
            )
            info["direct_children"] = len(os.listdir(target))
        else:
            info["extension"] = Path(target).suffix
            info["is_text"] = Path(target).suffix.lower() in TEXT_EXTENSIONS

        return {"success": True, "data": info}

    def _resolve(self, path: str) -> str:
        if os.path.isabs(path):
            return os.path.normpath(path)
        if path == '~':
            return self.base
        if path == '..':
            return os.path.dirname(self.cwd)
        if path.startswith('~/'):
            return os.path.normpath(os.path.join(self.base, path[2:]))
        return os.path.normpath(os.path.join(self.cwd, path))


fs_navigator = FSNavigator()
