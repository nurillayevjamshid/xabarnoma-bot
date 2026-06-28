# Xabarnoma Bot

Avtomatik yangiliklarni `@aniquz` va `@Geointriga_uz` Telegram kanallaridan olib, `@xabarnomaofficial` kanalga yuboradigan bot.

Bot **doimiy ishlaydigan jarayon** (`python main.py`) sifatida ishlaydi: har 2-4 daqiqada kanallarni tekshiradi va eng eski yuborilmagan postni topib, **bir martada faqat bitta** postni xronologik (kelgan) tartibda yuboradi. Shu sababli postlar birvarakay emas, bitta-bittadan, teng oraliqda tarqatiladi.

## O'rnatish

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Ishga tushirish

```powershell
python main.py
```

## Fayllar

- `config.py` — bot token, kanal, Telegram kanallar ro'yxati, sozlamalar
- `scraper.py` — Telegram kanallardan yangiliklar olish
- `dedup.py` — takroriy postlarni oldini olish (SQLite, har platforma alohida)
- `publisher.py` — Telegram kanalga yuborish
- `instagram.py` — Instagramga yuborish (rasmiy Graph API)
- `main.py` — Telegram va Instagram tsikllari (parallel)

## Instagram avto-post

Bot Telegramdan tashqari Instagramga ham (rasmiy **Instagram Graph API** orqali)
post joylashi mumkin. Bu rasmiy yo'l bo'lib, akkaunt bloklanmaydi.

### Talablar

1. **Instagram Business/Creator akkaunt** (oddiy akkaunt emas).
2. U **Facebook Page** ga ulangan bo'lishi kerak.
3. **Facebook Developer App** yaratib, `instagram_basic` va
   `instagram_content_publish` ruxsatlari bilan **uzoq muddatli access token**
   olinadi.
4. Instagram Business akkauntning **user ID** si aniqlanadi.

### Sozlash (environment variables)

```bash
export IG_ENABLED=1
export IG_ACCESS_TOKEN="<uzoq muddatli token>"
export IG_USER_ID="<instagram business user id>"
# Ixtiyoriy:
export IG_DAILY_LIMIT=25          # Instagram rasmiy limiti: kuniga 25 post
export IG_MIN_INTERVAL_SEC=3600   # post oralig'i (min)
export IG_MAX_INTERVAL_SEC=5400   # post oralig'i (max)
export IG_FOOTER="Telegram: @xabarnomaofficial"
```

### Muhim eslatmalar

- Instagram **faqat rasmli** postni qabul qiladi — rasmsiz (matnli) maqolalar
  Instagramga **o'tkazib yuboriladi**, faqat Telegramga ketadi.
- Instagram tezligi Telegramnikidan ancha sekin (kuniga 25 post limiti), shu
  sababli alohida, kamroq interval bilan ishlaydi.
- `IG_ENABLED` o'rnatilmasa yoki token/ID bo'lmasa, Instagram qismi o'chiq
  qoladi va bot avvalgidek faqat Telegramga post qiladi.
