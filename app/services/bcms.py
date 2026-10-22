import json
from datetime import date, datetime, timezone

from app.algorithms.scoring import bia_score, risk_score, evaluate_disruption
from app.repositories.records import Repository


class BCMS:
    def __init__(self, db):
        self.db = db
        self.repo = Repository(db)

    def save(self, table, data, record_id=None):
        data = {k: v.strip() if isinstance(v, str) else v for k, v in data.items()}
        if table == "continuity_plan":
            return self.save_plan(data, self.steps(record_id) if record_id else [], record_id)
        if table == "scenario":
            process_ids, plan_ids = self.scenario_links(record_id) if record_id else ([], [])
            return self.save_scenario(data, process_ids, plan_ids, record_id)
        required = {"organization": ["name"], "department": ["name"], "business_process": ["code", "name"],
                    "risk": ["title"], "recovery_strategy": ["name"], "continuity_plan": ["code", "name"], "scenario": ["name"]}
        for key in required.get(table, []):
            if not data.get(key):
                raise ValueError("Majburiy maydonlarni to‘ldiring.")
        if table == "bia_assessment":
            bia_score(**{k: data[k] for k in ("financial", "operational", "reputational", "compliance", "mtpd", "rto", "rpo")})
            existing = self.db.conn.execute("SELECT id FROM bia_assessment WHERE process_id=?", (data["process_id"],)).fetchone()
            if existing and record_id is None:
                record_id = existing[0]
        if table == "risk":
            risk_score(data["likelihood"], data["impact"])
        if table == "organization":
            rows = self.repo.all(table)
            record_id = rows[0]["id"] if rows else None
        if table == "continuity_plan":
            date.fromisoformat(data["review_date"])
            for field, related in (("risk_id", "risk"), ("strategy_id", "recovery_strategy")):
                if data.get(field) and self.repo.get(related, data[field])["process_id"] != data["process_id"]:
                    raise ValueError("Risk, strategiya va reja bitta jarayonga tegishli bo‘lsin.")
        # Changing a risk/strategy's process must preserve linked plan consistency.
        if record_id and table in ("risk", "recovery_strategy"):
            field = "risk_id" if table == "risk" else "strategy_id"
            if self.db.conn.execute(f"SELECT 1 FROM continuity_plan WHERE {field}=? AND process_id<>?", (record_id, data["process_id"])).fetchone():
                raise ValueError("Avval bog‘langan rejadagi jarayon bog‘lanishini o‘zgartiring.")
        return self.repo.save(table, data, record_id)

    def processes(self):
        rows = [dict(r) for r in self.db.conn.execute("""
            SELECT p.*, d.name AS department, b.financial,b.operational,b.reputational,b.compliance,b.mtpd,b.rto,b.rpo,
                   b.id AS bia_id FROM business_process p JOIN department d ON d.id=p.department_id
                   LEFT JOIN bia_assessment b ON b.process_id=p.id ORDER BY p.id""")]
        for r in rows:
            r["score"], r["category"] = (None, None) if r["bia_id"] is None else bia_score(**{k:r[k] for k in ("financial","operational","reputational","compliance","mtpd","rto","rpo")})
        return rows

    def rankings(self):
        return sorted([p for p in self.processes() if p["score"] is not None], key=lambda p: (-p["score"], p["rto"], p["code"]))

    def risks(self):
        processes = {p["id"]: p["name"] for p in self.repo.all("business_process")}
        rows = self.repo.all("risk")
        for r in rows:
            r["score"], r["category"] = risk_score(r["likelihood"], r["impact"])
            r["process"] = processes[r["process_id"]]
        return sorted(rows, key=lambda r: (-r["score"], r["id"]))

    def plans(self):
        rows = [dict(r) for r in self.db.conn.execute("""SELECT p.*, b.name AS process,
                  (SELECT count(*) FROM recovery_step s WHERE s.plan_id=p.id) AS steps,
                  (SELECT coalesce(sum(completed),0) FROM recovery_step s WHERE s.plan_id=p.id) AS completed
                  FROM continuity_plan p JOIN business_process b ON b.id=p.process_id ORDER BY p.id""")]
        for r in rows:
            r["completion"] = round(100*r["completed"]/r["steps"]) if r["steps"] else 0
            r["readiness"] = "Tayyor" if r["steps"] and r["completed"] == r["steps"] and r["responsible"] and r["objectives"] and r["resources"] and r["status"] == "Tasdiqlangan" and r["review_date"] >= date.today().isoformat() else "Ko‘rib chiqish kerak"
        return rows

    def steps(self, plan_id):
        return [dict(r) for r in self.db.conn.execute("SELECT * FROM recovery_step WHERE plan_id=? ORDER BY position", (plan_id,))]

    def save_plan(self, data, steps, record_id=None):
        # Outer savepoint makes fields and all ordered procedures atomic.
        self.db.conn.execute("SAVEPOINT plan_edit")
        try:
            # Repository.save uses connection context, so perform the cohesive write here.
            date.fromisoformat(data["review_date"])
            if not data["name"].strip() or not data["code"].strip():
                raise ValueError("Reja nomi va kodi majburiy.")
            for field, related in (("risk_id", "risk"), ("strategy_id", "recovery_strategy")):
                if data.get(field) and self.repo.get(related, data[field])["process_id"] != data["process_id"]:
                    raise ValueError("Risk va strategiya reja jarayoniga mos bo‘lsin.")
            allowed = "code name process_id risk_id strategy_id responsible objectives resources review_date status".split()
            if set(data) != set(allowed):
                raise ValueError("Reja maydonlari to‘liq emas.")
            values = [data[k].strip() if isinstance(data[k], str) else data[k] for k in allowed]
            if record_id is None:
                cur = self.db.conn.execute(f"INSERT INTO continuity_plan ({','.join(allowed)}) VALUES ({','.join('?' for _ in allowed)})", values)
                record_id = cur.lastrowid
            else:
                if self.db.conn.execute(f"UPDATE continuity_plan SET {','.join(k+'=?' for k in allowed)} WHERE id=?", values+[record_id]).rowcount != 1:
                    raise ValueError("Reja topilmadi.")
            # Do not allow plans selected by scenarios to drift to unrelated processes.
            if self.db.conn.execute("""SELECT 1 FROM scenario_plan sp WHERE sp.plan_id=? AND NOT EXISTS
                (SELECT 1 FROM scenario_affected_process ap WHERE ap.scenario_id=sp.scenario_id AND ap.process_id=?)""", (record_id, data["process_id"])).fetchone():
                raise ValueError("Reja tanlangan ssenariy jarayonlariga mos kelmaydi.")
            self.db.conn.execute("DELETE FROM recovery_step WHERE plan_id=?", (record_id,))
            for pos, step in enumerate(steps, 1):
                if not step["instruction"].strip():
                    raise ValueError("Tiklash bosqichi bo‘sh bo‘lmasin.")
                self.db.conn.execute("INSERT INTO recovery_step(plan_id,position,instruction,completed) VALUES(?,?,?,?)",
                                     (record_id,pos,step["instruction"].strip(),int(bool(step["completed"]))))
            self.db.conn.execute("RELEASE plan_edit")
            return record_id
        except Exception:
            self.db.conn.execute("ROLLBACK TO plan_edit")
            self.db.conn.execute("RELEASE plan_edit")
            raise

    def scenario_links(self, scenario_id):
        processes = [r[0] for r in self.db.conn.execute("SELECT process_id FROM scenario_affected_process WHERE scenario_id=?", (scenario_id,))]
        plans = [r[0] for r in self.db.conn.execute("SELECT plan_id FROM scenario_plan WHERE scenario_id=?", (scenario_id,))]
        return processes, plans

    def save_scenario(self, data, process_ids, plan_ids, record_id=None):
        from app.algorithms.scoring import number
        number(data["duration"], "Davomiylik", 0)
        if not data["name"].strip() or not process_ids:
            raise ValueError("Ssenariy nomi va kamida bitta jarayonni tanlang.")
        if any(self.repo.get("continuity_plan", pid)["process_id"] not in process_ids for pid in plan_ids):
            raise ValueError("Tanlangan rejalar ta’sirlangan jarayonlarga tegishli bo‘lsin.")
        columns = ["name","description","duration","resources","actions"]
        if set(data) != set(columns):
            raise ValueError("Ssenariy maydonlari noto‘g‘ri.")
        with self.db.conn:
            values = [data[k] for k in columns]
            if record_id is None:
                record_id = self.db.conn.execute("INSERT INTO scenario(name,description,duration,resources,actions) VALUES(?,?,?,?,?)", values).lastrowid
            elif self.db.conn.execute("UPDATE scenario SET name=?,description=?,duration=?,resources=?,actions=? WHERE id=?", values+[record_id]).rowcount != 1:
                raise ValueError("Ssenariy topilmadi.")
            self.db.conn.execute("DELETE FROM scenario_affected_process WHERE scenario_id=?", (record_id,))
            self.db.conn.execute("DELETE FROM scenario_plan WHERE scenario_id=?", (record_id,))
            self.db.conn.execute("DELETE FROM scenario_result WHERE scenario_id=?", (record_id,))
            self.db.conn.executemany("INSERT INTO scenario_affected_process VALUES(?,?)", [(record_id,p) for p in sorted(set(process_ids))])
            self.db.conn.executemany("INSERT INTO scenario_plan VALUES(?,?)", [(record_id,p) for p in sorted(set(plan_ids))])
        return record_id

    def evaluate(self, scenario_id):
        scenario = self.repo.get("scenario", scenario_id)
        ids, plan_ids = self.scenario_links(scenario_id)
        if not ids:
            raise ValueError("Ta’sirlangan jarayonlar tanlanmagan.")
        rows = evaluate_disruption(scenario["duration"], [p for p in self.processes() if p["id"] in ids])
        for r in rows:
            r["plans"] = [p["name"] for p in self.plans() if p["id"] in plan_ids and p["process_id"] == r["process_id"]]
            if not r["plans"]:
                r["recommendation"] += " Ushbu ssenariy uchun tiklanish rejasini belgilang."
        snapshot = {"scenario": scenario, "rows": rows, "plan_ids": plan_ids, "model": "Deterministik stol usti modeli; o‘lchangan tiklanish vaqti emas."}
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self.db.conn:
            self.db.conn.execute("INSERT INTO scenario_result(scenario_id,evaluated_at,result_json) VALUES(?,?,?)", (scenario_id,now,json.dumps(snapshot,ensure_ascii=False)))
        return self.latest_result(scenario_id)

    def latest_result(self, scenario_id):
        row = self.db.conn.execute("SELECT * FROM scenario_result WHERE scenario_id=? ORDER BY id DESC LIMIT 1", (scenario_id,)).fetchone()
        return dict(row, result=json.loads(row["result_json"])) if row else None

    def metrics(self):
        processes, risks = self.processes(), self.risks()
        return {"departments":len(self.repo.all("department")), "processes":len(processes),
                "critical":sum(p["category"] == "Critical" for p in processes),
                "bia":len(self.rankings()), "high_risks":sum(r["category"] in ("High","Critical") for r in risks),
                "plans":len(self.plans()), "scenarios":len(self.repo.all("scenario")),
                "assessments":self.db.conn.execute("SELECT count(DISTINCT scenario_id) FROM scenario_result").fetchone()[0]}
