# core/bot_utils.py
"""Utility helpers for bot error handling.
Provides a decorator `bot_error_handler` that catches any exception
raised inside a TeleBot handler, logs it via the terminal logger,
and sends a generic error message to the user.
"""
import functools
import logging
import traceback

# Re‑use the same logger defined in terminal_controller for consistency.
_audit_logger = logging.getLogger("nexum.terminal")


def bot_error_handler(func):
    """Decorator for Telegram bot handlers.
    Catches exceptions, logs detailed traceback, and replies with a
    user‑friendly message. The original function's signature is preserved.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Log full traceback for debugging.
            tb_str = traceback.format_exc()
            _audit_logger.error(f"Bot handler error in {func.__name__}: {e}\n{tb_str}")
            # Attempt to extract the TeleBot message object to reply.
            # Most handlers receive a single argument `message` or `call`.
            message = None
            for obj in args:
                if hasattr(obj, "chat") and hasattr(obj, "id"):
                    message = obj
                    break
            if message and hasattr(message, "chat"):
                try:
                    # Send a generic safe reply.
                    bot = getattr(message, "bot", None) or getattr(message, "_bot", None)
                    if bot:
                        bot.reply_to(message, "⚠️ حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى أو التواصل مع الدعم.")
                except Exception:
                    # If replying fails, silently ignore to avoid recursion.
                    pass
            # Re‑raise so that TeleBot's internal error handling can also act if needed.
            raise

    return wrapper
