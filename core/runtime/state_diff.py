import json
from typing import Dict, Any

class StateDiffEngine:
    """
    Runtime State Diff Engine
    بدلاً من إرسال حالة النظام بالكامل إلى الواجهة، يقوم بتوليد 
    (Patches/Delta) لتخفيف العبء عن الشبكة والذاكرة.
    """
    def __init__(self):
        self._last_known_state: Dict[str, Any] = {}

    def compute_diff(self, new_state: Dict[str, Any], namespace: str = "global") -> Dict[str, Any]:
        """توليد الفروقات بين الحالة السابقة والحالية"""
        last_state = self._last_known_state.get(namespace, {})
        diff = {}
        
        for key, value in new_state.items():
            if key not in last_state or last_state[key] != value:
                diff[key] = value
                
        # Update the known state
        self._last_known_state[namespace] = dict(new_state)
        
        return diff

state_diff = StateDiffEngine()
