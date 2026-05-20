from collections import defaultdict

class FSMManager:
    """
    مدير آلة الحالات المحدودة (FSM) لإدارة تدفق المحادثات وجلسات المستخدمين.
    """
    def __init__(self):
        # قاموس لحفظ حالة كل مستخدم، وهيكله: {user_id: state_name}
        self._states = defaultdict(lambda: "IDLE")
        # قاموس لحفظ البيانات المؤقتة لكل مستخدم خلال الجلسة
        self._data = defaultdict(dict)

    def set_state(self, user_id: int, state: str):
        """تعيين حالة مستخدم معين"""
        self._states[user_id] = state

    def get_state(self, user_id: int) -> str:
        """جلب الحالة الحالية للمستخدم"""
        return self._states[user_id]

    def clear(self, user_id: int):
        """تصفير حالة وبيانات المستخدم"""
        self._states[user_id] = "IDLE"
        self._data[user_id] = {}

    def update_data(self, user_id: int, **kwargs):
        """تحديث أو إضافة بيانات مؤقتة لجلسة المستخدم"""
        self._data[user_id].update(kwargs)

    def get_data(self, user_id: int) -> dict:
        """جلب البيانات المؤقتة الخاصة بالمستخدم"""
        return self._data[user_id]

fsm_manager = FSMManager()
