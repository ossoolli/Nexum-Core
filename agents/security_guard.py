import os
from core.system_tools import BASE_DIR

def scan_core_files():
    core_path = os.path.join(BASE_DIR, 'core')
    vulnerabilities = []
    for root, dirs, files in os.walk(core_path):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                    # Simple heuristic: check for dangerous patterns
                    if 'eval(' in content or 'os.system(' in content:
                        vulnerabilities.append(f'Potential vulnerability in {filepath}: Dangerous function found.')
    return vulnerabilities

if __name__ == '__main__':
    results = scan_core_files()
    for issue in results:
        print(issue)