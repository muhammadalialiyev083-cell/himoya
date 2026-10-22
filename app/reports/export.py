"""Offline Qt PDF rendering and spreadsheet-safe UTF-8 CSV."""
import csv
import html
import os
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QMarginsF
from PySide6.QtGui import QFont, QPageLayout, QPageSize, QPdfWriter, QTextDocument

from app.algorithms.scoring import CATEGORIES


def snapshot(service):
    orgs = service.repo.all("organization")
    plans = service.plans()
    return {"organization":orgs[0] if orgs else {"name":"Tashkilot belgilanmagan"},
            "generated":datetime.now().astimezone().isoformat(timespec="seconds"),
            "metrics":service.metrics(), "rankings":service.rankings(), "risks":service.risks(),
            "plans":plans, "steps":{p["id"]:service.steps(p["id"]) for p in plans},
            "strategies":service.repo.all("recovery_strategy"),
            "scenarios":[service.latest_result(s["id"]) for s in service.repo.all("scenario")]}


def esc(value):
    return html.escape(str(value if value is not None else "—")).replace("\n", "<br>")


def category(value):
    return CATEGORIES.get(value, value or "Baholanmagan")


def table(headers, rows):
    head = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body = "".join("<tr>"+"".join(f"<td>{esc(v)}</td>" for v in row)+"</tr>" for row in rows)
    if not rows:
        body = f'<tr><td colspan="{len(headers)}">Hozircha yozuvlar mavjud emas.</td></tr>'
    return f'<table width="100%" cellspacing="0" cellpadding="6"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def report_html(data, kind="assessment", plan_id=None):
    titles = {"assessment":"Biznes uzluksizligini baholash hisoboti", "register":"Risk va ustuvorlik reyestri", "plan":"Biznes uzluksizligi rejasi"}
    body = f'<h1>{titles[kind]}</h1><h2>{esc(data["organization"]["name"])}</h2><p>UzluksizBCMS Desktop 1.0.0 • {esc(data["generated"])}</p>'
    if kind == "plan":
        plan = next((p for p in data["plans"] if p["id"] == plan_id), None)
        if not plan:
            raise ValueError("Reja topilmadi.")
        body += f'<h2>{esc(plan["code"])} — {esc(plan["name"])}</h2>'
        fields = [("Jarayon",plan["process"]),("Mas’ul",plan["responsible"]),("Tiklanish maqsadlari",plan["objectives"]),
                  ("Resurslar",plan["resources"]),("Ko‘rib chiqish sanasi",plan["review_date"]),("Holat",plan["status"]),
                  ("Tayyorlik",plan["readiness"]),("Bajarilishi",f'{plan["completion"]}%')]
        body += table(["Maydon","Qiymat"],fields)
        risk = next((r for r in data["risks"] if r["id"] == plan["risk_id"]), None)
        strategy = next((r for r in data["strategies"] if r["id"] == plan["strategy_id"]), None)
        if risk:
            body += f'<p>Bog‘langan risk: {esc(risk["title"])} ({category(risk["category"])})</p>'
        if strategy:
            body += f'<h3>Strategiya: {esc(strategy["name"])}</h3><p>{esc(strategy["actions"])}</p>'
        body += '<h3>Raqamlangan tiklash tartibi</h3>' + table(["№","Amal","Bajarilgan"],[(s["position"],s["instruction"],"Ha" if s["completed"] else "Yo‘q") for s in data["steps"][plan_id]])
    else:
        m = data["metrics"]
        body += f'<h3>Umumiy ko‘rsatkichlar</h3><p>Jarayonlar: {m["processes"]}; bo‘limlar: {m["departments"]}; BIA: {m["bia"]}; kritik jarayonlar: {m["critical"]}; yuqori/kritik risklar: {m["high_risks"]}; rejalar: {m["plans"]}; baholangan ssenariylar: {m["assessments"]}.</p>'
        body += '<h3>Jarayonlar ustuvorligi</h3>' + table(["Kod","Jarayon","Ball","Daraja","RTO (s)","MTPD (s)","RPO (s)"],[(p["code"],p["name"],f'{p["score"]:.2f}',category(p["category"]),p["rto"],p["mtpd"],p["rpo"]) for p in data["rankings"]])
        body += '<h3>Risklar reyestri</h3>' + table(["Risk","Jarayon","Ehtimol","Ta’sir","Ball","Daraja","Tavsiya"],[(r["title"],r["process"],r["likelihood"],r["impact"],r["score"],category(r["category"]),r["action"] or ("Zudlik bilan choralar rejasini tuzing." if r["score"]>=16 else "Kamaytirish choralarini belgilang." if r["score"]>5 else "Davriy kuzating.")) for r in data["risks"]])
        if kind == "assessment":
            body += '<h3>Rejalar tayyorligi</h3>' + table(["Reja","Jarayon","Bosqichlar","Bajarilishi","Tayyorlik"],[(p["name"],p["process"],p["steps"],f'{p["completion"]}%',p["readiness"]) for p in data["plans"]])
            for result in data["scenarios"]:
                if result:
                    r = result["result"]
                    body += f'<h3>Ssenariy: {esc(r["scenario"]["name"])}</h3><p>{esc(result["evaluated_at"])} — {esc(r["model"])}</p>'
                    body += table(["Jarayon","Uzilish (s)","RTO buzildi","MTPD buzildi","Tavsiya"],[(p["name"],p["duration"],"BIA yo‘q" if p["rto_violation"] is None else "Ha" if p["rto_violation"] else "Yo‘q","BIA yo‘q" if p["mtpd_violation"] is None else "Ha" if p["mtpd_violation"] else "Yo‘q",p["recommendation"]) for p in r["rows"]])
            body += '<h3>Qoidaga asoslangan tavsiyalar</h3>'
            body += '<p>Baholanmagan jarayonlar uchun BIA o‘tkazing.</p>' if m["bia"] < m["processes"] else '<p>Barcha jarayonlar BIA bilan qamrab olingan.</p>'
            if m["high_risks"]:
                body += '<p>Yuqori va kritik risklar uchun mas’ul, kamaytirish chorasi va tiklash rejasini tekshiring.</p>'
            if any(p["readiness"] != "Tayyor" for p in data["plans"]):
                body += '<p>Rejalarni tasdiqlang, resurslar va bosqichlarni to‘ldiring, ko‘rib chiqish sanasini yangilang.</p>'
    body += '<h3>Metodologiya</h3><p>BIA = 20 × (0.30 × moliyaviy + 0.35 × operatsion + 0.20 × obro‘ + 0.15 × muvofiqlik). Kirishlar: 0–5. Chegaralar: 75 — kritik, 50 — yuqori, 25 — o‘rta; undan past — past. Teng ball: qisqaroq RTO birinchi.</p><p>Risk = ehtimollik × ta’sir (1–5). 1–5: past; 6–10: o‘rta; 11–15: yuqori; 16–25: kritik. Uzilish RTO yoki MTPDdan qat’iy katta bo‘lsa, tegishli maqsad buziladi. Resurslar qayd etiladi, vaqt kamayishi taxmin qilinmaydi. BIA bo‘lmasa, natija noma’lum.</p><p>Ushbu vazn va chegaralar dastur uchun belgilangan tadqiqot parametrlaridir. Ular rasmiy ISO formulalari emas. ISO sertifikati, to‘liq muvofiqlik yoki tajribada tasdiqlangan aniqlik da’vo qilinmaydi. NAMUNA yozuvlari haqiqiy tadqiqot natijalari emas. SQLite bazasi shifrlanmagan.</p>'
    return '<html><head><meta charset="utf-8"><style>body{font-family:"Segoe UI","DejaVu Sans",sans-serif;color:#162b40;font-size:10pt}h1{color:#087f73;font-size:21pt}h2{font-size:15pt}h3{color:#087f73}th{background:#133248;color:white;text-align:left}td{border-bottom:1px solid #dbe4e9}p{line-height:1.5}</style></head><body>'+body+'</body></html>'


def write_pdf(path, data, kind="assessment", plan_id=None):
    path = Path(path)
    writer = QPdfWriter(str(path))
    writer.setTitle("UzluksizBCMS — " + data["organization"]["name"])
    writer.setCreator("UzluksizBCMS Desktop 1.0.0")
    writer.setResolution(144)
    writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    writer.setPageMargins(QMarginsF(14,14,14,14), QPageLayout.Unit.Millimeter)
    doc = QTextDocument()
    doc.setDefaultFont(QFont("Segoe UI" if os.name == "nt" else "DejaVu Sans", 10))
    doc.setHtml(report_html(data, kind, plan_id))
    doc.print_(writer)
    del doc, writer
    if not path.is_file() or path.stat().st_size < 300 or path.read_bytes()[:5] != b"%PDF-":
        raise OSError("PDF yozilmadi.")
    return path


def spreadsheet_safe(value):
    text = str(value if value is not None else "")
    return "'" + text if text.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")) else text


def write_csv(path, data):
    with open(path, "w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream)
        writer.writerow([spreadsheet_safe(x) for x in ["Tashkilot",data["organization"]["name"],"Sana",data["generated"]]])
        writer.writerow(["Tur","Kod/nom","Jarayon","Ball","Daraja","RTO (soat)","MTPD (soat)","RPO (soat)","Tavsiya"])
        for p in data["rankings"]:
            writer.writerow([spreadsheet_safe(x) for x in ["BIA",p["code"],p["name"],p["score"],category(p["category"]),p["rto"],p["mtpd"],p["rpo"],"Kritik jarayon rejasini tekshiring." if p["category"]=="Critical" else "Davriy qayta baholang."]])
        for r in data["risks"]:
            writer.writerow([spreadsheet_safe(x) for x in ["Risk",r["title"],r["process"],r["score"],category(r["category"]),"","","",r["action"] or ("Zudlik bilan choralar belgilang." if r["score"]>=16 else "Kamaytirish choralarini ko‘rib chiqing." if r["score"]>5 else "Davriy kuzating.")]])
        writer.writerow(["Metodologiya","BIA=20*(0.30*F+0.35*O+0.20*R+0.15*C); Risk=L*I; tadqiqot parametrlari, rasmiy ISO formulasi emas."])
    return Path(path)
