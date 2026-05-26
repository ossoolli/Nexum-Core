import pytest
from unittest.mock import MagicMock, patch
from nexum.intelligence.classifier import LocalClassifier, Intent

def test_intent_classification():
    clf = LocalClassifier()
    
    # تصنيف محلي بالكلمات المفتاحية
    result = clf.classify("حالة النظام")
    assert result.intent == Intent.MONITOR
    assert result.confidence == 0.9

def test_fallback_on_default():
    clf = LocalClassifier()
    
    # رسالة عادية بدون كلمات مفتاحية — يجب أن يعود للدردشة
    result = clf.classify("مرحبا كيف حالك")
    assert result.intent == Intent.CHAT

