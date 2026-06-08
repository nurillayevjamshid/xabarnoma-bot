# Xabarnoma Bot

Avtomatik yangiliklarni `@aniquz` va `@Geointriga_uz` Telegram kanallaridan olib, `@xabarnomaofficial` kanalga 5-10 daqiqa oralig'ida yuboradigan bot.

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
