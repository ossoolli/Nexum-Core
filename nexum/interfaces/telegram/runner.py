import json
import time
import logging
from pathlib import Path
from nexum.config import config

logger = logging.getLogger(__name__)
_STATE_FILE = config.storage_dir / "runtime_state.json"

class TelegramRunner:
    """
    يشغّل البوت مع:
    - crash recovery تلقائي
    - حفظ الحالة (pending_commands, last_analysis) على disk
    """
    def __init__(self, bot):
        self.bot = bot
        self._state = self._load_state()

    def _load_state(self) -> dict:
        if _STATE_FILE.exists():
            try:
                return json.loads(_STATE_FILE.read_text())
            except Exception:
                pass
        return {"pending_commands": {}, "last_analysis": {}}

    def save_state(self):
        try:
            _STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            _STATE_FILE.write_text(
                json.dumps(self._state, ensure_ascii=False, indent=2)
            )
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    @property
    def pending_commands(self) -> dict:
        return self._state["pending_commands"]

    @property
    def last_analysis(self) -> dict:
        return self._state["last_analysis"]

    def run(self):
        while True:
            try:
                logger.info("🔱 NEXUM Telegram Runner: Polling started")
                self.bot.infinity_polling(
                    timeout=30,
                    long_polling_timeout=25,
                    restart_on_change=False,
                )
            except KeyboardInterrupt:
                logger.info("Graceful shutdown requested")
                self.save_state()
                break
            except Exception as e:
                logger.error(f"Telegram Runner Crash: {e}", exc_info=True)
                self.save_state()
                time.sleep(10)
