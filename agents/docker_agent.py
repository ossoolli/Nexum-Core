import html
import subprocess
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from core.executor import executor


class DockerAgent:
    """وكيل مخصص لإدارة Docker المتقدمة من خلال البوت أو لوحة التحكم"""

    def _run(self, cmd: str) -> dict:
        result = executor.execute(cmd, force=True)
        return result

    def get_containers_list(self) -> list:
        """إرجاع قائمة الحاويات كقائمة من القواميس"""
        res = self._run("docker ps -a --format '{{.Names}}|{{.Status}}|{{.Ports}}|{{.Image}}|{{.ID}}'")
        if res['status'] != 'success':
            return []
            
        containers = []
        for line in res['output'].strip().split('\n'):
            if not line: continue
            parts = line.split('|')
            if len(parts) >= 5:
                containers.append({
                    "name": parts[0],
                    "status": parts[1],
                    "ports": parts[2],
                    "image": parts[3],
                    "id": parts[4]
                })
        return containers

    def get_images_list(self) -> list:
        res = self._run("docker images --format '{{.Repository}}|{{.Tag}}|{{.Size}}|{{.ID}}'")
        if res['status'] != 'success':
            return []
            
        images = []
        for line in res['output'].strip().split('\n'):
            if not line: continue
            parts = line.split('|')
            if len(parts) >= 4:
                images.append({
                    "name": parts[0],
                    "tag": parts[1],
                    "size": parts[2],
                    "id": parts[3]
                })
        return images

    def get_container_logs(self, container_name: str, tail: int = 50) -> str:
        safe_name = container_name.replace(';','').replace('&','').replace('|','')
        res = self._run(f"docker logs --tail {tail} {safe_name}")
        return res['output']

    def restart_container(self, container_name: str) -> bool:
        safe_name = container_name.replace(';','').replace('&','').replace('|','')
        res = self._run(f"docker restart {safe_name}")
        return res['status'] == 'success'

    def stop_container(self, container_name: str) -> bool:
        safe_name = container_name.replace(';','').replace('&','').replace('|','')
        res = self._run(f"docker stop {safe_name}")
        return res['status'] == 'success'
        
    def start_container(self, container_name: str) -> bool:
        safe_name = container_name.replace(';','').replace('&','').replace('|','')
        res = self._run(f"docker start {safe_name}")
        return res['status'] == 'success'

    def get_stats(self) -> str:
        res = self._run("docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}'")
        return res['output']
        
    def system_prune(self) -> str:
        res = self._run("docker system prune -af")
        return res['output']

docker_agent = DockerAgent()
