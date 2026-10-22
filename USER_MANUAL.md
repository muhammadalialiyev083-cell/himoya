# UzluksizBCMS Desktop — Foydalanuvchi qo‘llanmasi

Versiya: **1.0.0 MVP**. Asosiy til: o‘zbek lotin. Internet kerak emas.

## 1. Ishga tushirish va kirish

Windows relizi qurilgach, `UzluksizBCMS.exe` faylini shaxsiy yozish ruxsati bo‘lgan papkadan oching. Birinchi ochilishda administrator nomi va kamida 10 belgili parolni ikki marta kiriting. Dastur parolning tuzlangan xeshini saqlaydi; asl parolni saqlamaydi. Keyingi ochilishlarda shu hisob bilan kiring. Parolni unutish uchun yashirin standart parol mavjud emas; parol va ishonchli zaxira nusxani xavfsiz saqlang.

## 2. Tashkilot va bo‘limlar

`Tashkilot` → `Profilni yaratish / tahrirlash`: nom, soha, tavsif va mas’ulni kiriting. Bitta faol tashkilot mavjud. Pastdagi jadvaldan bo‘lim qo‘shing, tahrirlang yoki o‘chiring. Jarayon biriktirilgan bo‘limni o‘chirish bloklanadi. Umumiy statistikani `Boshqaruv paneli`dan ko‘ring.

## 3. Biznes jarayonlari

`Biznes jarayonlari` → `Qo‘shish`: noyob kod, nom va bo‘limni tanlang; tavsif, mas’ul, resurslar, ITga bog‘liqlik va holatni to‘ldiring. Qidiruv barcha ko‘rinadigan qiymatlar bo‘yicha ishlaydi. Daraja filtri BIA natijasiga asoslanadi. Jadval satrini ikki marta bosish tafsilotlar, risklar va rejalarni ko‘rsatadi. Tahrirlash va o‘chirishdan oldin satrni tanlang.

Bog‘langan risk, reja, strategiya yoki ssenariy bo‘lsa, jarayonni o‘chirish bloklanadi. Ularni avval o‘chiring yoki qayta bog‘lang. Jarayon bilan birga uning yagona BIA yozuvi o‘chiriladi; tasdiqlash oynasi bu haqda ogohlantiradi.

## 4. BIA tahlili

Jarayonni tanlang va moliyaviy, operatsion, obro‘ hamda huquqiy ta’sirlarni 0–5 oralig‘ida kiriting. MTPD va RTO musbat; RTO ≤ MTPD; RPO ≥ 0. Vaqtlar soatda. RPO alohida maqsad va RTOdan avtomatik ko‘chirilmaydi. Bir jarayon uchun bitta joriy BIA mavjud; qayta qo‘shish shu bahoni yangilaydi.

Ball: `20 × (0.30×moliyaviy + 0.35×operatsion + 0.20×obro‘ + 0.15×huquqiy)`. 75+: kritik, 50+: yuqori, 25+: o‘rta, undan past: past. Ballari teng jarayonlardan RTOsi qisqaroq bo‘lgani oldin turadi. Jadval qiymatlari va `Tafsilot` orqali izohni, boshqaruv panelida ustuvorlik diagrammasini ko‘ring. Bu tadqiqot modeli, rasmiy ISO formulasi emas.

## 5. Risklarni baholash

Risk nomi, jarayon, tahdid, zaiflik, ehtimollik va ta’sir (1–5), himoya chorasi, egasi, tavsiya va holatni kiriting. Ball = ehtimollik × ta’sir. 1–5 past, 6–10 o‘rta, 11–15 yuqori, 16–25 kritik. Matritsada satr ehtimollikni, ustun ta’sirni bildiradi; katak `ball · risklar soni`ni ko‘rsatadi. Katakka sichqonchani olib borish risk nomlarini ko‘rsatadi. Matritsa va ko‘rsatkichlar o‘zgarishdan so‘ng yangilanadi. Dashboard barcha qayd etilgan risklarni, jumladan yopiq risklarni sanaydi; holat reyestrda ko‘rsatiladi.

## 6. Strategiyalar va uzluksizlik rejalari

`Uzluksizlik rejalari` ichidagi `Tiklanish strategiyalari` sahifasida jarayon, amallar, resurslar, mas’ul va ustuvorlikni belgilang (1 — eng yuqori). Rejalar sahifasida noyob kod, nom, jarayon, ixtiyoriy risk/strategiya, mas’ul, tiklanish maqsadi, resurs, ko‘rib chiqish sanasi va holatni to‘ldiring. Risk va strategiya shu jarayonga tegishli bo‘lishi kerak; tanlovlar mos ravishda cheklanadi.

Pastdagi jadvalda `Bosqich` tugmasi bilan tiklash amallarini qo‘shing, matnini tahrirlang, yuqoriga/pastga ko‘chiring, bajarilganini belgilang. Saqlash reja va bosqichlarni bitta tranzaksiyada yozadi. Bajarilishi — belgilangan bosqichlar ulushi; haqiqiy hodisada o‘lchangan tiklanish vaqti emas.

`Tayyor` holati: kamida bitta bosqich bor, barcha bosqichlar bajarilgan, mas’ul/maqsad/resurslar mavjud, reja tasdiqlangan va ko‘rib chiqish sanasi o‘tmagan. Aks holda `Ko‘rib chiqish kerak`. Tanlangan reja PDFga eksport qilinadi; PDF ko‘ruvchidan chop eting.

## 7. Stol usti simulyatsiyasi

`Simulyatsiya` → `Qo‘shish`: nom, tavsif, kutilayotgan uzilish soati, mavjud resurslar, javob amallari, ta’sirlangan jarayonlar va qo‘llaniladigan rejalarni belgilang. Elektr uzilishi, ma’lumotlar markazi ishdan chiqishi, ransomware, tarmoq uzilishi yoki xodim yo‘qligi kabi ssenariylarni kiriting.

Satrni tanlab `Ssenariyni baholash`ni bosing. Uzilish RTOdan katta bo‘lsa RTO buzilishi, MTPDdan katta bo‘lsa MTPD buzilishi qayd etiladi. Tenglik buzilish emas. BIA bo‘lmasa xulosa `BIA yo‘q` bo‘ladi. Resurslar qayd etiladi, lekin model ularga qarab vaqtni o‘zi qisqartirmaydi. Tanlangan rejalar jarayon bilan mos bo‘lishi kerak.

`Saqlangan natija` baholash paytidagi vaqtli nusxani ochadi. BIA yoki reja o‘zgarganidan keyin qayta baholang. Ssenariyning o‘zi tahrirlansa, eski natijalar olib tashlanadi va qayta baholash talab etiladi. Bu haqiqiy kiberhujum yoki infratuzilma simulyatori emas.

## 8. Hisobotlar

`Hisobotlar`da to‘liq baholash PDFi, risk/ustuvorlik PDFi yoki CSVni tanlang. Saqlash manzilini o‘zingiz belgilang; mavjud fayl bo‘lsa fayl oynasida almashtirishni tasdiqlang. Hisobot fon vazifasida yaratiladi. Tugagach, pastdagi holat satrida manzil ko‘rinadi. Hisobot tugamaguncha dasturni yopish bloklanadi. PDFlar o‘zbek matnini shrift bilan birga saqlaydi; CSV UTF-8 BOMda yoziladi.

## 9. Zaxira, tiklash va namuna

`Sozlamalar` → `Baza zaxira nusxasini saqlash`: alohida `.sqlite3` faylini tanlang. Asosiy bazaning o‘zini zaxira manzili sifatida tanlash bloklanadi. Fayl barcha ma’lumotlar va administrator xeshini saqlaydi. Uni maxfiy joyda saqlang.

`Tekshirilgan zaxiradan tiklash`: nusxani tanlang va almashtirishni tasdiqlang. Dastur versiya, tuzilma, yaxlitlik va tashqi kalitlarni tekshiradi. Joriy holat avtomatik `backups/before-restore-...sqlite3` fayliga saqlanadi. Keyin nusxa tiklanadi va undagi hisob bilan qayta kirish talab etiladi. Noto‘g‘ri yoki yangi versiya bazasi qabul qilinmaydi. Administrator parolini almashtirish amaldagi parolni talab etadi.

`NAMUNA to‘plamini qo‘shish` ixtiyoriy: mavjud tashkilotni almashtirmaydi. Yozuvlar `NAMUNA` deb belgilangan; ular haqiqiy ilmiy natijalar emas. Takroran qo‘shish bloklanadi. O‘chirishda avval ssenariy, reja, strategiya va risklarni, keyin jarayon va bo‘limni olib tashlang; har bir o‘chirish tasdiqlanadi.

## 10. Ma’lumotlar manzili va cheklovlar

Windows bazasi: `%LOCALAPPDATA%\UzluksizBCMS\uzluksiz.sqlite3`. Fayl shifrlanmagan. Windows foydalanuvchi huquqlari va disk shifrlashi orqali himoyalang. Dastur bitta mahalliy administrator uchun; tarmoqda birgalikda ishlash ko‘zda tutilmagan. Batafsil chegaralar: `docs/KNOWN_LIMITATIONS.md`.
