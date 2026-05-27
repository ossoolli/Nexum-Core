# -*- coding: utf-8 -*-
# protocols/agent_contract.py
"""
🛡️ AgentContract — عقد بروتوكول تبادل الرسائل والتحقق بين الوكلاء السياديين (v1.0.0)
====================================================================================
- يوفر تمثيلاً برمجياً متوافقاً مع بروتوكول Protobuf (protocols/agent_contract.proto).
- يضمن سلامة البيانات (Data Integrity) والتحقق من المخطط (Schema Validation) للأحداث وقرارات المحاكمة.
- يدعم التشفير الآمن والترميز الثنائي (Base64 Binary-safe encoding) لنقل الحمولة البرمجية (Payloads).
"""

import json
import uuid
import time
import base64
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger(__name__)

@dataclass
class AgentEvent:
    """
    عقد الحدث المتبادل بين الوكلاء السياديين.
    مستوحى من رسالة AgentEvent في ملف Protobuf.
    """
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender: str = ""
    timestamp: str = field(default_factory=lambda: time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    topic: str = ""
    payload: bytes = b""  # ترميز ثنائي آمن للحمولة الإضافية

    def to_dict(self) -> Dict[str, Any]:
        """تحويل الكائن إلى قاموس برمز آمن للبيانات الثنائية (base64)"""
        return {
            "event_id": self.event_id,
            "sender": self.sender,
            "timestamp": self.timestamp,
            "topic": self.topic,
            "payload": base64.b64encode(self.payload).decode("utf-8") if isinstance(self.payload, bytes) else self.payload
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentEvent':
        """إنشاء كائن من القاموس مع فك ترميز البيانات الثنائية"""
        payload_data = data.get("payload", b"")
        if isinstance(payload_data, str):
            try:
                payload_bytes = base64.b64decode(payload_data.encode("utf-8"))
            except Exception:
                payload_bytes = payload_data.encode("utf-8")
        else:
            payload_bytes = payload_data

        return cls(
            event_id=data.get("event_id", str(uuid.uuid4())),
            sender=data.get("sender", ""),
            timestamp=data.get("timestamp", time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())),
            topic=data.get("topic", ""),
            payload=payload_bytes
        )

    def serialize(self) -> str:
        """سلسلة الكائن إلى نص JSON"""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def deserialize(cls, json_str: str) -> 'AgentEvent':
        """فك سلسلة نص JSON إلى كائن"""
        return cls.from_dict(json.loads(json_str))


@dataclass
class DeliberationRequest:
    """
    طلب عقد جلسة محاكمة واتخاذ قرار من مجلس الحكماء.
    مستوحى من رسالة DeliberationRequest في ملف Protobuf.
    """
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    prompt: str = ""
    context_code: str = ""
    requested_by: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DeliberationRequest':
        return cls(
            task_id=data.get("task_id", str(uuid.uuid4())),
            prompt=data.get("prompt", ""),
            context_code=data.get("context_code", ""),
            requested_by=data.get("requested_by", "")
        )

    def serialize(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def deserialize(cls, json_str: str) -> 'DeliberationRequest':
        return cls.from_dict(json.loads(json_str))


@dataclass
class ModelVote:
    """
    صوت نموذج منفرد داخل مجلس الحكماء.
    مستوحى من رسالة ModelVote في ملف Protobuf.
    """
    model_id: str = ""
    approved: bool = False
    reasoning: str = ""
    output_code: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelVote':
        return cls(
            model_id=data.get("model_id", ""),
            approved=data.get("approved", False),
            reasoning=data.get("reasoning", ""),
            output_code=data.get("output_code", "")
        )


@dataclass
class DeliberationVerdict:
    """
    القرار النهائي الصادر عن مجلس الحكماء بعد التوافق.
    مستوحى من رسالة DeliberationVerdict في ملف Protobuf.
    """
    task_id: str = ""
    approved: bool = False
    votes: List[ModelVote] = field(default_factory=list)
    merged_output: str = ""
    consensus_grade: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "approved": self.approved,
            "votes": [v.to_dict() for v in self.votes],
            "merged_output": self.merged_output,
            "consensus_grade": self.consensus_grade
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DeliberationVerdict':
        raw_votes = data.get("votes", [])
        votes_list = []
        for v in raw_votes:
            if isinstance(v, dict):
                votes_list.append(ModelVote.from_dict(v))
            elif isinstance(v, ModelVote):
                votes_list.append(v)

        return cls(
            task_id=data.get("task_id", ""),
            approved=data.get("approved", False),
            votes=votes_list,
            merged_output=data.get("merged_output", ""),
            consensus_grade=data.get("consensus_grade", "")
        )

    def serialize(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def deserialize(cls, json_str: str) -> 'DeliberationVerdict':
        return cls.from_dict(json.loads(json_str))


class AgentContractValidator:
    """
    أداة للتحقق من تطابق الرسائل المتبادلة مع عقود النظام السيادية.
    """
    @staticmethod
    def validate_event(event: Any) -> bool:
        """التحقق من صحة كائن الحدث"""
        if not isinstance(event, AgentEvent):
            logger.error("[ContractValidator] Object is not an instance of AgentEvent.")
            return False
        if not event.event_id or not event.sender or not event.topic:
            logger.warning(f"[ContractValidator] Event missing critical metadata: id={event.event_id}, sender={event.sender}, topic={event.topic}")
            return False
        return True

    @staticmethod
    def validate_verdict(verdict: Any) -> bool:
        """التحقق من صحة قرار مجلس الحكماء"""
        if not isinstance(verdict, DeliberationVerdict):
            logger.error("[ContractValidator] Object is not an instance of DeliberationVerdict.")
            return False
        if not verdict.task_id or not verdict.consensus_grade:
            logger.warning(f"[ContractValidator] Verdict missing critical metadata: task_id={verdict.task_id}, grade={verdict.consensus_grade}")
            return False
        return True
