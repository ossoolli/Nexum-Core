import subprocess
import os

class SandboxRuntime:
    """
    Secure Sandbox Runtime
    بيئة العزل الصارمة. لا يوجد وكيل يقوم بتنفيذ كود برمجي خارج هذه النواة (Docker/gVisor).
    """

    def __init__(self, use_gvisor=False):
        self.use_gvisor = use_gvisor

    def execute_in_sandbox(self, agent_id: str, script_content: str, language="python"):
        """
        ينفذ الكود داخل حاوية Docker معزولة لمنع الوكلاء من إختراق النظام الأساسي.
        """
        # في بيئة الإنتاج: استخدم gVisor (runsc)
        runtime_flag = "--runtime=runsc" if self.use_gvisor else ""
        container_name = f"sandbox_{agent_id}_{os.urandom(4).hex()}"
        
        if language == "python":
            cmd = (
                f"docker run --rm --name {container_name} {runtime_flag} "
                f"--network none --memory 256m --cpus 0.5 "
                f"python:3.10-alpine python -c \"{script_content.replace('\"', '\\\"')}\""
            )
        else:
            return {"status": "error", "message": f"Language {language} not supported yet in sandbox"}
        
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=60
            )
            return {
                "status": "success" if result.returncode == 0 else "failed",
                "output": result.stdout + result.stderr,
                "agent_id": agent_id
            }
        except subprocess.TimeoutExpired:
            return {"status": "error", "output": "Sandbox execution timeout", "agent_id": agent_id}
        except Exception as e:
            return {"status": "error", "output": str(e), "agent_id": agent_id}

sandbox = SandboxRuntime()
