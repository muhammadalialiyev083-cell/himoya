# Dastur tavsifi — EHM ro‘yxatidan o‘tkazishga tayyorgarlik uchun

**Nomi:** UzluksizBCMS Desktop — Business Continuity Management System. **Versiya:** 1.0.0 MVP.

**Ilmiy mavzu:** “Tashkilotlarda biznes uzluksizligini boshqarish tizimini loyihalash dasturini ishlab chiqish.”

**Maqsad:** tashkilotning muhim biznes jarayonlarini qayd etish, uzilish ta’sirini ball bilan baholash, risklar va tiklash rejalarini bog‘lash, stol usti ssenariylarini qoidalar asosida tahlil qilish va tahliliy hisobotlarni mahalliy shakllantirish.

**Foydalanuvchilar:** biznes uzluksizligi bo‘yicha mas’ullar, risk menejerlari, kichik tashkilot administratorlari, ilmiy tadqiqotchilar va o‘quv namoyishi ishtirokchilari. MVP bir mahalliy administrator va bir faol tashkilot uchun mo‘ljallangan.

**Funksional modullar:** tashkilot/bo‘limlar, biznes jarayonlari, BIA, risklarni baholash, tiklanish strategiyalari va uzluksizlik rejalari, stol usti ssenariylari, boshqaruv paneli va PDF/CSV hisobotlari. Qo‘shimcha imkoniyatlar: mahalliy autentifikatsiya, zaxira va tekshirilgan tiklash, namunaviy ma’lumotlar.

**Texnologiyalar:** Python 3.12 x64; PySide6 6.9.3/Qt Widgets; SQLite/sqlite3; QSS; Qt PDF; CSV; pytest; PyInstaller. Windows 10/11 x64 — maqsadli tarqatish tizimi. Linux muhitida manba va paket tekshiruvlari bajariladi; Windows EXE holati `TEST_RESULTS.md` va `WINDOWS_RELEASE.md`da alohida qayd etiladi.

**Arxitektura va baza:** `ARCHITECTURE.md` va `app/database/schema.sql`. **Algoritmlar:** `ALGORITHMS.md`. **Ishlatish:** `../USER_MANUAL.md`. **O‘rnatish/yig‘ish:** `WINDOWS_RELEASE.md`. **Sinov dalillari:** `TEST_RESULTS.md` hamda `../release/test-results.xml`. **Fayllar ro‘yxati:** `SOURCE_INVENTORY.md`.

**Original loyihalardan ajratish:** loyiha yangi `UzluksizBCMS-Desktop` papkasida yaratiladi; mavjud `himoya` Git loyihasi o‘zgartirilmaydi. Virtual muhit, manbalar va yig‘ish mahsulotlari faqat yangi loyiha ichida. Oxirgi foydalanuvchining ma’lumotlari shaxsiy application data papkasida.

**Skrinshotlar:** `release/source-smoke-final/dashboard.png` — Qtning Linux offscreen rejimida olingan haqiqiy oyna tasviri, NAMUNA yozuvlari bilan. Windowsda tizimning skrinshot vositasidan foydalanib kirish oynasi, bo‘limlar, BIA, matritsa, reja, ssenariy natijasi va hisobotlarni tasvirga oling; shaxsiy ma’lumotlarni oshkor qilmang. Sinov hisobotlari papkasidagi PDFlar namuna chiqishlaridir.

**Huquqiy va ilmiy holat:** ushbu hujjat ro‘yxatdan o‘tkazish uchun keyinchalik tayyorlanadigan materiallarga yordamchi tavsifdir. Mualliflik rekvizitlari va topshirish talablari huquq egasi tomonidan to‘ldiriladi. DGU ro‘yxatidan o‘tganlik, ISO sertifikati yoki to‘liq standart muvofiqligi da’vo qilinmaydi. Tahlil vaznlari dasturdagi tadqiqot parametrlari, rasmiy standart formulalari emas.
