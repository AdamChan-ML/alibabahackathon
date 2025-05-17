import sqlite3
from datetime import datetime

class ExpenseDB:
    def __init__(self, db_path="expenses.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_table()

    def create_table(self):
        self.conn.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            source TEXT,
            date TEXT,
            amount REAL,
            category TEXT,
            description TEXT,
            is_tax_deductible BOOLEAN,
            suggested_claim TEXT,
            matched_rule TEXT,
            created_at TEXT
        )
        ''')
        self.conn.commit()

    def add_expense(self, user_id, source, date, amount, category, description, is_tax_deductible, suggested_claim, matched_rule):
        self.conn.execute('''
        INSERT INTO expenses (
            user_id, source, date, amount, category, description,
            is_tax_deductible, suggested_claim, matched_rule, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, source, date, amount, category, description,
            is_tax_deductible, suggested_claim, matched_rule,
            datetime.now().isoformat()
        ))
        self.conn.commit()

    def get_expenses_by_user(self, user_id):
        cursor = self.conn.execute('''
        SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC
        ''', (user_id,))
        return cursor.fetchall()

    def get_summary_by_category(self, user_id):
        cursor = self.conn.execute('''
        SELECT category, SUM(amount) FROM expenses
        WHERE user_id = ? GROUP BY category
        ''', (user_id,))
        return cursor.fetchall()

    def close(self):
        self.conn.close()
