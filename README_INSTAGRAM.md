# Telegram to Instagram Auto-Poster

Ushbu loyiha Telegram kanaldagi yangi postlarni avtomatik ravishda Instagram akkauntingizga joylash uchun mo'ljallangan.

## Xususiyatlari
- **Telethon**: Telegram kanallarini kuzatish uchun.
- **Playwright**: Instagram Web orqali post joylash uchun (Graph API-siz).
- **Media Group**: Albomlarni (Carousel) to'liq qo'llab-quvvatlaydi.
- **Sessiya boshqaruvi**: `storage_state.json` orqali login holatini saqlaydi.
- **Asinxron**: `asyncio` yordamida tez va samarali ishlaydi.

## O'rnatish

1. Kerakli kutubxonalarni o'rnating:
   ```bash
   pip install -r requirements_insta.txt
   playwright install chromium
   ```

2. `.env` faylini yarating va quyidagi ma'lumotlarni kiriting:
   ```env
   API_ID=your_telegram_api_id
   API_HASH=your_telegram_api_hash
   SESSION_NAME=xabarnoma_session
   SOURCE_CHANNEL=telegram_channel_username
   INSTAGRAM_USERNAME=your_instagram_username
   INSTAGRAM_PASSWORD=your_instagram_password
   ```

## Ishga tushirish

1. Birinchi marta Instagram-ga login qilish uchun:
   ```bash
   python login.py
   ```
   Bu buyruq brauzerni ochadi va siz login qilishingiz kerak bo'ladi. Muvaffaqiyatli login bo'lgach, sessiya saqlanadi.

2. Asosiy botni ishga tushirish:
   ```bash
   python main_insta.py
   ```

## Loyiha Tuzilmasi
- `main_insta.py`: Asosiy ishga tushiruvchi fayl.
- `config_insta.py`: Sozlamalar.
- `telegram_client.py`: Telegram-dan postlarni yuklab olish.
- `instagram_client.py`: Instagram-ga post joylash.
- `login.py`: Birinchi login uchun skript.
- `utils.py`: Yordamchi funksiyalar va loglar.
