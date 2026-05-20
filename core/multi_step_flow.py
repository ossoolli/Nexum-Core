import time

class MultiStepFlowManager:
    """
    يدير العمليات التي تتطلب عدة خطوات للحصول على معلومات من المستخدم
    """
    def __init__(self):
        self.active_flows = {} # {user_id: {"name": str, "step": int, "data": dict, "expiry": float}}

    def start_flow(self, user_id: int, flow_name: str):
        self.active_flows[user_id] = {
            "name": flow_name,
            "step": 1,
            "data": {},
            "expiry": time.time() + 600 # 10 mins
        }

    def get_flow(self, user_id: int):
        flow = self.active_flows.get(user_id)
        if flow and time.time() > flow["expiry"]:
            del self.active_flows[user_id]
            return None
        return flow

    def next_step(self, user_id: int, input_data: str, field_name: str):
        flow = self.active_flows.get(user_id)
        if not flow: return False
        
        flow["data"][field_name] = input_data
        flow["step"] += 1
        flow["expiry"] = time.time() + 600
        return True

    def cancel_flow(self, user_id: int):
        self.active_flows.pop(user_id, None)

flow_manager = MultiStepFlowManager()
