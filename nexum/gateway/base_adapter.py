from abc import ABC, abstractmethod

class PlatformAdapter(ABC):
    @abstractmethod
    def listen(self):
        pass

    @abstractmethod
    def send_message(self, chat_id: str, text: str):
        pass

    @abstractmethod
    def format_message(self, message: str) -> str:
        pass
