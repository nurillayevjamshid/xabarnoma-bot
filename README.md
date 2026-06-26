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
- `dedup.py` — takroriy postlarni oldini olish (SQLite)
- `publisher.py` — Telegram kanalga yuborish
- `main.py` — asosiy tsikl
