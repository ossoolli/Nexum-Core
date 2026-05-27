import os
import logging
from pathlib import Path
from nexum.config import config

logger = logging.getLogger("nexum.kernel")

def bootstrap():
    """
    تهيئة بيئة النظام قبل التشغيل الفعلي.
    """
    logger.info("🔱 Bootstrapping NEXUM Sovereign OS...")

    # 1. التأكد من المجلدات الأساسية
    required_dirs = [
        config.storage_dir,
        config.storage_dir / "logs",
        config.storage_dir / "docs",
        config.storage_dir / "temp",
        Path("registry/apps"),
        Path("registry/bots"),
        Path("registry/agents"),
    ]

    for d in required_dirs:
        if not d.exists():
            logger.info(f"Creating directory: {d}")
            d.mkdir(parents=True, exist_ok=True)

    # 2. فحص المتغيرات الحرجة
    if not config.telegram_token or config.telegram_token == "your_bot_token_here":
        logger.error("❌ TELEGRAM_TOKEN is missing or default. System will not start.")
        return False

    if not config.google_api_key and not config.agent_platform_api_key:
        logger.warning("⚠️ GOOGLE_API_KEY / AGENT_PLATFORM_API_KEY is missing. Intelligence features will be disabled.")

    # 3. طباعة تقرير البداية
    logger.info(f"✅ Kernel Initialized. Mode: Sovereign.")
    logger.info(f"📂 Storage: {config.storage_dir}")
    logger.info(f"👤 Admin ID: {config.admin_id}")
    
    return True
