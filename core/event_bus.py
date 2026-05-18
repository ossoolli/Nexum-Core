"""
NEXUM Event Bus — Realtime Event-Driven Architecture
ناقل الأحداث الحية. يتم توجيه كل الأحداث عبر النسخة الموزعة.
"""
from core.event_bus_distributed import DistributedEventBus, event_bus

# Export the singleton and the class for compatibility
__all__ = ['event_bus', 'DistributedEventBus', 'NexumEventBus']

# For backward compatibility if someone expects NexumEventBus type
NexumEventBus = DistributedEventBus
