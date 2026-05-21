"""
core/fs_search.py
محرك البحث الداخلي — يبحث في الأسماء والمحتوى والأحجام والتواريخ
"""
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List
from core.env_config import BASE_DIR
from core.fs_control import TEXT_EXTENSIONS


class FSSearch:
    def __init__(self):
        self.base = BASE_DIR

    def by_name(self, pattern: str, root: str = None,
                case_sensitive: bool = False,
                file_type: str = 'any') -> dict:
        """
        يبحث عن ملفات بالاسم أو الامتداد.
        pattern: نص عادي أو glob (*) أو regex.
        file_type: 'file' | 'dir' | 'any'
        """
        search_root = root or self.base
        if not os.path.exists(search_root):
            return {"success": False, "error": f"مجلد البحث غير موجود: {search_root}"}

        results = []
        flags = 0 if case_sensitive else re.IGNORECASE

        # تحويل glob لـ regex
        if '*' in pattern or '?' in pattern:
            regex_pat = pattern.replace('.', r'\.').replace('*', '.*').replace('?', '.')
        else:
            regex_pat = re.escape(pattern)

        try:
            compiled = re.compile(regex_pat, flags)
        except re.error:
            return {"success": False, "error": f"نمط بحث غير صالح: {pattern}"}

        for dirpath, dirnames, filenames in os.walk(search_root):
            # تخطي مجلدات venv والـ git
            dirnames[:] = [d for d in dirnames if d not in {'.git', 'venv', '__pycache__', 'node_modules', '.env'}]

            items = []
            if file_type in ('file', 'any'):
                items.extend([(f, 'file', dirpath) for f in filenames])
            if file_type in ('dir', 'any'):
                items.extend([(d, 'dir', dirpath) for d in dirnames])

            for name, itype, parent in items:
                if compiled.search(name):
                    full = os.path.join(parent, name)
                    try:
                        st = os.stat(full)
                        results.append({
                            "name": name,
                            "type": itype,
                            "path": full,
                            "relative": os.path.relpath(full, self.base),
                            "size_kb": round(st.st_size / 1024, 2) if itype == 'file' else None,
                            "modified": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")
                        })
                    except Exception:
                        pass

        return {
            "success": True,
            "pattern": pattern,
            "root": search_root,
            "count": len(results),
            "results": results[:100]  # أقصى 100 نتيجة
        }

    def by_content(self, query: str, root: str = None,
                   extensions: List[str] = None,
                   case_sensitive: bool = False,
                   max_results: int = 50) -> dict:
        """
        يبحث في محتوى الملفات النصية.
        يعيد اسم الملف + رقم السطر + السطر الذي يحتوي البحث.
        """
        search_root = root or self.base
        allowed_ext = set(extensions) if extensions else TEXT_EXTENSIONS
        flags = 0 if case_sensitive else re.IGNORECASE

        try:
            compiled = re.compile(re.escape(query), flags)
        except re.error:
            return {"success": False, "error": f"نمط بحث غير صالح"}

        results = []
        files_scanned = 0

        for dirpath, dirnames, filenames in os.walk(search_root):
            dirnames[:] = [d for d in dirnames if d not in {'.git', 'venv', '__pycache__', 'node_modules'}]

            for fname in filenames:
                ext = Path(fname).suffix.lower()
                if ext not in allowed_ext and fname not in allowed_ext:
                    continue

                full = os.path.join(dirpath, fname)
                files_scanned += 1

                try:
                    with open(full, 'r', encoding='utf-8', errors='ignore') as f:
                        for lineno, line in enumerate(f, 1):
                            if compiled.search(line):
                                results.append({
                                    "file": os.path.relpath(full, self.base),
                                    "line_number": lineno,
                                    "line_content": line.strip()[:200],
                                    "match": query
                                })
                                if len(results) >= max_results:
                                    break
                except Exception:
                    pass

                if len(results) >= max_results:
                    break

        return {
            "success": True,
            "query": query,
            "files_scanned": files_scanned,
            "matches_found": len(results),
            "results": results,
            "truncated": len(results) >= max_results
        }

    def by_size(self, root: str = None,
                min_kb: float = None,
                max_kb: float = None,
                sort_desc: bool = True) -> dict:
        """يبحث عن ملفات بالحجم"""
        search_root = root or self.base
        results = []

        for dirpath, dirnames, filenames in os.walk(search_root):
            dirnames[:] = [d for d in dirnames if d not in {'.git', 'venv', '__pycache__'}]
            for fname in filenames:
                full = os.path.join(dirpath, fname)
                try:
                    size_kb = os.path.getsize(full) / 1024
                    if min_kb and size_kb < min_kb:
                        continue
                    if max_kb and size_kb > max_kb:
                        continue
                    results.append({
                        "file": os.path.relpath(full, self.base),
                        "size_kb": round(size_kb, 2),
                        "modified": datetime.fromtimestamp(os.path.getmtime(full)).strftime("%Y-%m-%d %H:%M")
                    })
                except Exception:
                    pass

        results.sort(key=lambda x: x['size_kb'], reverse=sort_desc)
        return {
            "success": True,
            "count": len(results),
            "results": results[:50],
            "total_kb": round(sum(r['size_kb'] for r in results), 2)
        }

    def recent(self, root: str = None,
               days: int = 1,
               limit: int = 30) -> dict:
        """يعرض الملفات المعدّلة خلال آخر N أيام"""
        search_root = root or self.base
        cutoff = datetime.now() - timedelta(days=days)
        results = []

        for dirpath, dirnames, filenames in os.walk(search_root):
            dirnames[:] = [d for d in dirnames if d not in {'.git', 'venv', '__pycache__'}]
            for fname in filenames:
                full = os.path.join(dirpath, fname)
                try:
                    mtime = datetime.fromtimestamp(os.path.getmtime(full))
                    if mtime >= cutoff:
                        results.append({
                            "file": os.path.relpath(full, self.base),
                            "modified": mtime.strftime("%Y-%m-%d %H:%M:%S"),
                            "size_kb": round(os.path.getsize(full) / 1024, 2)
                        })
                except Exception:
                    pass

        results.sort(key=lambda x: x['modified'], reverse=True)
        return {
            "success": True,
            "days": days,
            "count": len(results),
            "results": results[:limit]
        }


fs_search = FSSearch()
