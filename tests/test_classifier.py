import pytest
from unittest.mock import MagicMock, patch
from nexum.intelligence.classifier import GeminiClassifier, Intent

def test_intent_classification():
    clf = GeminiClassifier()
    
    # محاكاة رد JSON من الجمناي
    mock_response = '{"intent":"monitor","confidence":0.95,"reasoning":"سؤال عن النظام"}'
    
    with patch("services.gemini_service.gemini_service.ask", return_value=(mock_response, None)):
        result = clf.classify("حالة النظام")
        assert result.intent == Intent.MONITOR
        assert result.confidence == 0.95

def test_fallback_on_error():
    clf = GeminiClassifier()
    
    # محاكاة فشل الـ API
    with patch("services.gemini_service.gemini_service.ask", side_effect=Exception("API down")):
        result = clf.classify("أي رسالة")
        assert result.intent == Intent.CHAT  # يجب أن يعود للدردشة كخيار آمن
