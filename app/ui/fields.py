def fields_for(table, service):
    repo = service.repo
    refs = lambda t, label="name": [(r[label],r["id"]) for r in repo.all(t)]
    process = ("process_id","Biznes jarayoni *","choice",refs("business_process"))
    line = lambda k,l: (k,l,"line",None)
    text = lambda k,l: (k,l,"text",None)
    choice = lambda k,l,values: (k,l,"choice",[(v,v) for v in values])
    definitions = {
      "organization":[line("name","Tashkilot nomi *"),line("industry","Faoliyat sohasi"),text("description","Tavsif"),line("responsible","Mas’ul shaxs")],
      "department":[line("name","Bo‘lim nomi *"),line("responsible","Mas’ul shaxs")],
      "business_process":[line("code","Noyob jarayon kodi *"),line("name","Jarayon nomi *"),text("description","Tavsif"),("department_id","Bo‘lim *","choice",refs("department")),line("responsible","Mas’ul shaxs"),text("resources","Muhim resurslar"),text("it_dependency","ITga bog‘liqlik"),choice("status","Holat",["Faol","To‘xtatilgan","Qayta ko‘rib chiqish"])],
      "bia_assessment":[process,("financial","Moliyaviy ta’sir (0–5)","impact",(0,5)),("operational","Operatsion ta’sir (0–5)","impact",(0,5)),("reputational","Obro‘ga ta’sir (0–5)","impact",(0,5)),("compliance","Huquqiy ta’sir (0–5)","impact",(0,5)),("mtpd","MTPD (soat) *","number",(0,1000000)),("rto","RTO (soat) *","number",(0,1000000)),("rpo","RPO (soat)","number",(0,1000000))],
      "risk":[line("title","Risk nomi *"),process,text("threat","Tahdid"),text("vulnerability","Zaiflik"),("likelihood","Ehtimollik (1–5)","integer",(1,5)),("impact","Ta’sir (1–5)","integer",(1,5)),text("mitigation","Mavjud himoya choralari"),line("owner","Risk egasi"),text("action","Tavsiya etilgan chora"),choice("status","Holat",["Ochiq","Kamaytirilmoqda","Yopiq"])],
      "recovery_strategy":[line("name","Strategiya nomi *"),process,text("actions","Tiklash amallari"),text("resources","Kerakli resurslar"),line("responsible","Mas’ul shaxs"),("priority","Ustuvorlik (1 — eng yuqori)","integer",(1,5))],
      "continuity_plan":[line("code","Noyob reja kodi *"),line("name","Reja nomi *"),process,("risk_id","Bog‘langan risk","choice",[("Bog‘lanmagan",None)]+refs("risk","title")),("strategy_id","Tiklanish strategiyasi","choice",[("Bog‘lanmagan",None)]+refs("recovery_strategy")),line("responsible","Mas’ul shaxs"),text("objectives","Tiklanish maqsadlari (RTO/RPO)"),text("resources","Resurslar"),("review_date","Keyingi ko‘rib chiqish","date",None),choice("status","Holat",["Loyiha","Tasdiqlangan","Arxiv"])],
      "scenario":[line("name","Ssenariy nomi *"),text("description","Tavsif"),("duration","Kutilayotgan uzilish (soat)","number",(0,1000000)),text("resources","Mavjud tiklanish resurslari"),text("actions","Kutilayotgan javob amallari"),("process_ids","Ta’sirlangan jarayonlar *","multi",refs("business_process")),("plan_ids","Qo‘llaniladigan rejalar","multi",refs("continuity_plan"))]
    }
    return definitions[table]


LABELS = {"name":"Nomi","code":"Kod","description":"Tavsif","industry":"Soha","responsible":"Mas’ul","department":"Bo‘lim","resources":"Resurslar","it_dependency":"ITga bog‘liqlik","status":"Holat","score":"Ball","category":"Daraja","mtpd":"MTPD (soat)","rto":"RTO (soat)","rpo":"RPO (soat)","financial":"Moliyaviy","operational":"Operatsion","reputational":"Obro‘","compliance":"Muvofiqlik","title":"Risk nomi","threat":"Tahdid","vulnerability":"Zaiflik","likelihood":"Ehtimollik","impact":"Ta’sir","mitigation":"Himoya choralari","owner":"Risk egasi","action":"Tavsiya","process":"Jarayon","actions":"Amallar","priority":"Ustuvorlik","objectives":"Maqsadlar","review_date":"Ko‘rib chiqish","steps":"Bosqichlar","completed":"Bajarilgan","completion":"Bajarilishi (%)","readiness":"Tayyorlik","duration":"Uzilish (soat)"}
