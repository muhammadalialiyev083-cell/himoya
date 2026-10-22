"""Application-defined research rules; these are not official ISO formulae."""
import math

WEIGHTS = {"financial": .30, "operational": .35, "reputational": .20, "compliance": .15}
CATEGORIES = {"Critical": "Kritik", "High": "Yuqori", "Medium": "O‘rta", "Low": "Past"}
COLORS = {"Critical": "#b42335", "High": "#b35b0b", "Medium": "#887000", "Low": "#087f68"}


def number(value, label, low=None, high=None):
    try:
        n = float(value)
    except (ValueError, TypeError):
        raise ValueError(f"{label}: son kiriting.") from None
    if not math.isfinite(n) or (low is not None and n < low) or (high is not None and n > high):
        raise ValueError(f"{label}: qiymat ruxsat etilgan oraliqda emas.")
    return n


def bia_category(score):
    return "Critical" if score >= 75 else "High" if score >= 50 else "Medium" if score >= 25 else "Low"


def bia_score(financial, operational, reputational, compliance, mtpd, rto, rpo):
    values = dict(zip(WEIGHTS, (financial, operational, reputational, compliance)))
    for key, value in values.items():
        values[key] = number(value, key, 0, 5)
    mtpd, rto, rpo = number(mtpd, "MTPD"), number(rto, "RTO"), number(rpo, "RPO", 0)
    if mtpd <= 0 or rto <= 0 or rto > mtpd:
        raise ValueError("MTPD va RTO musbat bo‘lsin; RTO MTPDdan oshmasin.")
    score = round(20 * sum(WEIGHTS[k] * v for k, v in values.items()), 6)
    return score, bia_category(score)


def risk_score(likelihood, impact):
    l, i = number(likelihood, "Ehtimollik", 1, 5), number(impact, "Ta’sir", 1, 5)
    if not l.is_integer() or not i.is_integer():
        raise ValueError("Risk ballari 1–5 oralig‘ida butun son bo‘lsin.")
    score = int(l * i)
    category = "Critical" if score >= 16 else "High" if score >= 11 else "Medium" if score >= 6 else "Low"
    return score, category


def evaluate_disruption(duration, assessments):
    duration = number(duration, "Uzilish davomiyligi", 0)
    rows = []
    for process in assessments:
        row = {"process_id": process["id"], "name": process["name"], "duration": duration}
        if process.get("rto") is None:
            row.update(rto=None, mtpd=None, rto_violation=None, mtpd_violation=None,
                       recommendation="BIA tahlilini bajaring; tiklanish chegaralari belgilanmagan.")
        else:
            rto, mtpd = process["rto"], process["mtpd"]
            row.update(rto=rto, mtpd=mtpd, rto_violation=duration > rto, mtpd_violation=duration > mtpd)
            row["recommendation"] = ("MTPD oshdi: muqobil faoliyatni faollashtiring." if duration > mtpd else
                                     "RTO oshdi: tiklanish resurslarini kuchaytiring." if duration > rto else
                                     "Belgilangan vaqt maqsadlari ichida; rejani mashq qiling.")
        rows.append(row)
    return rows
