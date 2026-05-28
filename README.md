# Xabarnoma Bot

Avtomatik yangiliklarni `kun.uz`, `qalampir.uz`, `aniq.uz` saytlaridan olib, `@xabarnomaofficial` kanalga 5-10 daqiqa oralig'ida yuboradigan bot.

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

- `config.py` — bot token, kanal, sozlamalar
- `scraper.py` — yangiliklarni 3 ta saytdan olish
- `dedup.py` — takroriy postlarni oldini olish (SQLite)
- `publisher.py` — Telegram kanalga yuborish
- `main.py` — asosiy tsikl
