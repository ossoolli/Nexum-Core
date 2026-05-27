import yaml
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ProtocolEngine:
    """
    ينفذ workflows معرّفة بـ YAML.
    يدعم: تبعيات بين الخطوات، شروط، استبدال متغيرات.
    """
    def __init__(self, protocols_dir: Path):
        self.protocols_dir = protocols_dir

    def load_protocol(self, name: str) -> dict:
        path = self.protocols_dir / f"{name}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Protocol {name} not found")
        return yaml.safe_load(path.read_text(encoding="utf-8"))

    async def execute(self, protocol_name: str, context: dict) -> dict:
        protocol = self.load_protocol(protocol_name)
        results = {}

        logger.info(f"Starting execution of protocol: {protocol_name}")

        for step in protocol["steps"]:
            # 1. تحقق من التبعيات
            deps = step.get("depends_on", [])
            if not all(d in results for d in deps):
                logger.warning(f"Step {step['id']} skipped (missing deps)")
                continue

            # 2. تحقق من الشرط
            condition = step.get("condition")
            if condition and not self._eval_condition(condition, context, results):
                logger.info(f"Step {step['id']} skipped (condition false)")
                continue

            # 3. حل المتغيرات
            inputs = self._resolve_inputs(step["input"], context, results)

            # 4. التنفيذ الفعلي عبر tool_registry
            try:
                from core.tool_registry import tool_registry
                logger.info(f"Step {step['id']}: Executing tool {step['tool']}")
                res = tool_registry.execute_tool(step['tool'], inputs)
                results[step['id']] = res if isinstance(res, dict) else {"status": "success", "data": res}
            except Exception as e:
                logger.error(f"Step {step['id']} failed: {e}")
                results[step['id']] = {"status": "error", "error": str(e)}

        return results

    def _resolve_inputs(self, raw: dict, context: dict, results: dict) -> dict:
        """يحل {{variables}} في القواميس المتداخلة"""
        import re
        def resolve(val):
            if not isinstance(val, str):
                return val
            matches = re.findall(r"\{\{(.+?)\}\}", val)
            for match in matches:
                parts = match.strip().split(".")
                src = {**context, **results}
                
                # البحث في العمق
                target = src
                try:
                    for p in parts:
                        target = target.get(p, {})
                    val = val.replace("{{" + match + "}}", str(target))
                except:
                    pass
            return val
        return {k: resolve(v) for k, v in raw.items()}

    def _eval_condition(self, cond: str, context: dict, results: dict) -> bool:
        """تقييم بسيط للشرط"""
        try:
            # حل المتغيرات أولاً
            resolved = self._resolve_inputs({"c": cond}, context, results)["c"]
            return str(resolved).lower() not in ("false", "0", "", "none")
        except:
            return True

# Singleton context initialized later
