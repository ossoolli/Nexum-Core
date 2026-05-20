from typing import Dict, Any, Optional

# تخزين لحالة كل مستخدم 
# الهيكل: { user_id: {"state": "STATE_NAME", "data": {}} }
_USER_STATES: Dict[int, Dict[str, Any]] = {}

class FSMManager:
    """ مدير الحالات (State Machine) للعمليات المتسلسلة """
    
    @staticmethod
    def set_state(user_id: int, state: str):
        if user_id not in _USER_STATES:
            _USER_STATES[user_id] = {"state": None, "data": {}}
        _USER_STATES[user_id]["state"] = state

    @staticmethod
    def get_state(user_id: int) -> Optional[str]:
        return _USER_STATES.get(user_id, {}).get("state")

    @staticmethod
    def clear_state(user_id: int):
        if user_id in _USER_STATES:
            _USER_STATES[user_id]["state"] = None
            _USER_STATES[user_id]["data"] = {}

    @staticmethod
    def save_data(user_id: int, key: str, value: Any):
        if user_id not in _USER_STATES:
            _USER_STATES[user_id] = {"state": None, "data": {}}
        _USER_STATES[user_id]["data"][key] = value

    @staticmethod
    def get_data(user_id: int, key: str, default: Any = None) -> Any:
        return _USER_STATES.get(user_id, {}).get("data", {}).get(key, default)
        
    @staticmethod
    def get_all_data(user_id: int) -> dict:
        return _USER_STATES.get(user_id, {}).get("data", {})

fsm = FSMManager()
