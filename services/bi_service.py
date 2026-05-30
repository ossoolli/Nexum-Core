import sqlite3
import os
import logging
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class BIService:
    def __init__(self, db_path="/home/madarmutaz/Nexum-Core/storage/nexum_business.db"):
        self.db_path = db_path

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def add_transaction(self, t_type: str, amount: float, currency: str, description: str, category: str):
        conn = self._get_connection()
        cursor = conn.cursor()
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO transactions (date, type, amount, currency, description, category)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (date, t_type, amount, currency, description, category))
        conn.commit()
        conn.close()
        return True

    def get_balance(self, currency="USD"):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT SUM(amount) FROM transactions WHERE type="income" AND currency=?', (currency,))
        income = cursor.fetchone()[0] or 0
        cursor.execute('SELECT SUM(amount) FROM transactions WHERE type="expense" AND currency=?', (currency,))
        expense = cursor.fetchone()[0] or 0
        conn.close()
        return income - expense

    def get_weekly_summary(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        # Simple weekly fetch (last 7 days)
        cursor.execute("SELECT * FROM transactions WHERE date >= date('now', '-7 days')")
        columns = [column[0] for column in cursor.description]
        transactions = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        cursor.execute("SELECT * FROM clients WHERE status='active'")
        columns = [column[0] for column in cursor.description]
        clients = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return {"transactions": transactions, "clients": clients}

    def add_client(self, name: str, email: str, phone: str = "", company: str = "", status: str = "active"):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO clients (name, email, phone, company, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, email, phone, company, status))
        conn.commit()
        conn.close()
        return True

bi_service = BIService()
