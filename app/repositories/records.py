"""Allowlisted identifiers; every user-supplied value is parameterized."""
TABLE_FIELDS = {
    "organization": "name industry description responsible",
    "department": "name responsible",
    "business_process": "code name description department_id responsible resources it_dependency status",
    "bia_assessment": "process_id financial operational reputational compliance mtpd rto rpo",
    "risk": "title process_id threat vulnerability likelihood impact mitigation owner action status",
    "recovery_strategy": "name process_id actions resources responsible priority",
    "continuity_plan": "code name process_id risk_id strategy_id responsible objectives resources review_date status",
    "scenario": "name description duration resources actions",
}


class Repository:
    def __init__(self, db):
        self.db = db

    def _table(self, table):
        if table not in TABLE_FIELDS:
            raise ValueError("Noma’lum jadval.")
        return table

    def all(self, table):
        return [dict(r) for r in self.db.conn.execute(f"SELECT * FROM {self._table(table)} ORDER BY id")]

    def get(self, table, record_id):
        row = self.db.conn.execute(f"SELECT * FROM {self._table(table)} WHERE id=?", (record_id,)).fetchone()
        if row is None:
            raise ValueError("Yozuv topilmadi; jadvalni yangilang.")
        return dict(row)

    def save(self, table, data, record_id=None):
        self._table(table)
        allowed = TABLE_FIELDS[table].split()
        if not data or set(data) - set(allowed):
            raise ValueError("Noma’lum yoki bo‘sh maydonlar.")
        columns = list(data)
        with self.db.conn:
            if record_id is None:
                cur = self.db.conn.execute(
                    f"INSERT INTO {table} ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                    [data[c] for c in columns])
                return cur.lastrowid
            cur = self.db.conn.execute(f"UPDATE {table} SET {','.join(c+'=?' for c in columns)} WHERE id=?",
                                       [data[c] for c in columns] + [record_id])
            if cur.rowcount != 1:
                raise ValueError("Yozuv topilmadi.")
            return record_id

    def delete(self, table, record_id):
        with self.db.conn:
            cur = self.db.conn.execute(f"DELETE FROM {self._table(table)} WHERE id=?", (record_id,))
            if cur.rowcount != 1:
                raise ValueError("Yozuv topilmadi.")
