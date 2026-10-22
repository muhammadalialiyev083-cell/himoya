"""Optional examples; never replace or alter the user's organization/data."""
from datetime import date, timedelta


def add_demo(service):
    repo = service.repo
    if any(p["code"] == "NAMUNA-01" for p in repo.all("business_process")):
        raise ValueError("NAMUNA to‘plami allaqachon mavjud; takroran qo‘shilmadi.")
    if not repo.all("organization"):
        service.save("organization", {"name":"NAMUNA — Samarqand Servis", "industry":"Xizmat ko‘rsatish", "description":"Faqat o‘quv va namoyish ma’lumotlari.", "responsible":"NAMUNA — administrator"})
    dep = service.save("department", {"name":"NAMUNA — Operatsiyalar", "responsible":"NAMUNA — bo‘lim boshlig‘i"})
    pid = service.save("business_process", {"code":"NAMUNA-01","name":"NAMUNA — Buyurtmalarni qayta ishlash","description":"O‘quv misoli","department_id":dep,"responsible":"NAMUNA — operator","resources":"Ishchi kompyuterlar, zaxira elektr","it_dependency":"Mahalliy buyurtmalar bazasi","status":"Faol"})
    service.save("bia_assessment",dict(process_id=pid,financial=4,operational=5,reputational=3,compliance=3,mtpd=24,rto=4,rpo=1))
    rid = service.save("risk",dict(title="NAMUNA — Elektr uzilishi",process_id=pid,threat="Elektr ta’minoti to‘xtashi",vulnerability="Bitta elektr manbai",likelihood=4,impact=4,mitigation="UPS mavjud",owner="NAMUNA — muhandis",action="Generator va qayta tiklash mashqi",status="Ochiq"))
    sid = service.save("recovery_strategy",dict(name="NAMUNA — Muqobil ish joyi",process_id=pid,actions="Zaxira ofisga ko‘chish",resources="Noutbuklar, aloqa",responsible="NAMUNA — koordinator",priority=1))
    plan = service.save_plan(dict(code="NAMUNA-BCP-01",name="NAMUNA — Buyurtmalar uzluksizligi",process_id=pid,risk_id=rid,strategy_id=sid,responsible="NAMUNA — koordinator",objectives="RTO 4 soat, RPO 1 soat",resources="UPS, noutbuk, zaxira nusxa",review_date=(date.today()+timedelta(days=365)).isoformat(),status="Tasdiqlangan"),[{"instruction":"Hodisani qayd etish va mas’ulni xabardor qilish","completed":True},{"instruction":"Zaxira elektr va muqobil ish joyini faollashtirish","completed":False},{"instruction":"Bazani tekshirish va xizmatni tiklash","completed":False}])
    scenario = service.save_scenario(dict(name="NAMUNA — Elektr uzilishi",description="Stol usti mashqi",duration=8,resources="UPS va noutbuk",actions="Muqobil ish joyiga o‘tish"),[pid],[plan])
    service.evaluate(scenario)
    return pid
