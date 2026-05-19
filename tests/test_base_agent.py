import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.base_agent import BaseAgent, AgentStatus

class DummyAgent(BaseAgent):
    def run(self, input_data):
        return {"status": "ok", "echo": input_data.get("msg", "")}

def test_lifecycle():
    a = DummyAgent("test", "test agent")
    assert a.status == AgentStatus.IDLE
    result = a.start({"msg": "hello"})
    assert result["status"] == "ok"
    assert a.status == AgentStatus.IDLE
    a.pause()
    assert a.status == AgentStatus.PAUSED
    a.resume()
    assert a.status == AgentStatus.IDLE
    a.terminate()
    assert a.status == AgentStatus.TERMINATED
    print("test_lifecycle PASSED")

def test_health():
    a = DummyAgent("health_test", "")
    assert a.health_check() == True
    a.terminate()
    assert a.health_check() == False
    print("test_health PASSED")

def test_metrics():
    a = DummyAgent("metrics_test", "")
    a.record_metric("score", 99)
    status = a.get_status()
    assert status["metrics"]["score"] == 99
    assert "uptime_seconds" in status
    print("test_metrics PASSED")

if __name__ == "__main__":
    test_lifecycle()
    test_health()
    test_metrics()
    print("ALL TESTS PASSED")
