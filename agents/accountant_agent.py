import os
import json
import logging
from datetime import datetime
from typing import Dict, Any
from core.base_agent import BaseAgent
from services.gemini_service import gemini_service
from services.bi_service import bi_service

logger = logging.getLogger(__name__)

class AccountantAgent(BaseAgent):
    """
    AccountantAgent — الذكاء الإداري
    مسؤول عن تسجيل المعاملات المالية وتوليد التقارير.
    """

    def __init__(self):
        super().__init__(
            name="accountant_agent",
            description="وكيل الحسابات والذكاء الإداري (Sovereign Accountant)",
            version="1.0"
        )

    def process_financial_input(self, text: str) -> str:
        """تحليل النص المالي عبر Gemini وتسجيله"""
        prompt = f"""
        حلل النص المالي التالي واستخرج البيانات في تنسيق JSON:
        الكلمات المفتاحية: type (income/expense), amount (number), currency (e.g. USD, SAR, EUR), description, category.
        
        النص: "{text}"
        
        أعد JSON فقط.
        """
        response, _ = gemini_service.ask(prompt)
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            data = json.loads(json_match.group())
            
            # حفظ في قاعدة البيانات
            bi_service.add_transaction(
                t_type=data.get("type", "income"),
                amount=float(data.get("amount", 0)),
                currency=data.get("currency", "USD"),
                description=data.get("description", ""),
                category=data.get("category", "general")
            )
            
            balance = bi_service.get_balance(data.get("currency", "USD"))
            return f"✅ تم تسجيل المعاملة: {data.get('amount')} {data.get('currency')} ({data.get('description')}). الرصيد الحالي: {balance} {data.get('currency')}"
        except Exception as e:
            self.log(f"Financial parsing failed: {e}", level="ERROR")
            return "❌ فشل تحليل أو تسجيل المعاملة المالية."

    def generate_weekly_pdf(self) -> str:
        """توليد تقرير PDF أسبوعي"""
        try:
            from fpdf import FPDF
            summary = bi_service.get_weekly_summary()
            
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "Nexum Business Weekly Report", ln=True, align='C')
            pdf.ln(10)
            
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
            pdf.ln(5)
            
            # Transactions
            pdf.cell(0, 10, "Recent Transactions:", ln=True)
            pdf.set_font("Arial", '', 10)
            for t in summary["transactions"]:
                pdf.cell(0, 8, f"{t['date']} | {t['type']} | {t['amount']} {t['currency']} | {t['description']}", ln=True)
            
            pdf.ln(10)
            # Active Clients
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Active Clients:", ln=True)
            pdf.set_font("Arial", '', 10)
            for c in summary["clients"]:
                pdf.cell(0, 8, f"{c['name']} ({c['company']}) - {c['email']}", ln=True)
            
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            report_path = os.path.join(base_dir, "storage", "reports", f"weekly_{os.getpid()}.pdf")
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            pdf.output(report_path)
            return report_path
        except Exception as e:
            self.log(f"PDF generation failed: {e}", level="ERROR")
            return ""

    def run(self, input_data: dict) -> dict:
        text = input_data.get("text")
        action = input_data.get("action", "record")
        
        if action == "report":
            path = self.generate_weekly_pdf()
            return {"status": "success", "file_path": path}
            
        if not text:
            return {"status": "error", "error": "نص المعاملة مطلوب"}
            
        result = self.process_financial_input(text)
        return {"status": "success", "message": result}

accountant_agent = AccountantAgent()
