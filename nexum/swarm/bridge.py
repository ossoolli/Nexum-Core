import os
import json
import logging

class Bridge:
    """
    Inter-agent dialogue bridge for Nexum-Core and Summarizer-Bot.
    Uses a file-based IPC queue for structured messaging.
    """
    def __init__(self, bridge_path: str = "/home/madarmutaz/Nexum-Core/storage/bridge"):
        self.bridge_path = bridge_path
        os.makedirs(self.bridge_path, exist_ok=True)
        self.inbox = os.path.join(self.bridge_path, "inbox.jsonl")
        self.outbox = os.path.join(self.bridge_path, "outbox.jsonl")
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("Bridge")

    def send_message(self, sender: str, receiver: str, message: str, metadata: dict = {}):
        """Send a message through the bridge."""
        payload = {
            "sender": sender,
            "receiver": receiver,
            "message": message,
            "metadata": metadata,
        }
        with open(self.outbox, "a") as f:
            f.write(json.dumps(payload) + "\n")
        self.logger.info(f"Message sent from {sender} to {receiver}")

    def read_messages(self, agent_name: str):
        """Read pending messages for an agent."""
        # Simple implementation: read from outbox, maybe filter?
        # In a real system, this would involve atomicity and removal/archiving
        if not os.path.exists(self.outbox):
            return []
        
        with open(self.outbox, "r") as f:
            messages = [json.loads(line) for line in f if json.loads(line).get("receiver") == agent_name]
        return messages

if __name__ == "__main__":
    bridge = Bridge()
    bridge.send_message("Nexum-Core", "Summarizer-Bot", "Hello from Nexum-Core!")
    print("Bridge initialized and message sent.")
