from nexum.swarm.bridge import Bridge
import os
import json

def test_bridge_interaction():
    bridge = Bridge(bridge_path="/home/madarmutaz/Nexum-Core/storage/test_bridge")
    bridge.send_message("Nexum-Core", "Summarizer-Bot", "Please summarize current logs.", {"priority": "high"})
    
    messages = bridge.read_messages("Summarizer-Bot")
    assert len(messages) > 0
    assert messages[0]["sender"] == "Nexum-Core"
    assert messages[0]["message"] == "Please summarize current logs."
    print("Test passed: Bridge interaction verified.")

if __name__ == "__main__":
    test_bridge_interaction()
