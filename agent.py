from google import genai
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters
)
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
Sen 1C:Enterprise 8.3 bo'yicha senior dasturchi va mentorsan.

Ekspert yo'nalishlaring:
- 1C Enterprise 8.3
- KD2 (Конвертация данных 2)
- Общий модуль
- Объектный модуль
- Запросlar
- Регистры
- СКД
- HTTP-servis va REST API
- ERP integratsiyasi
- Telegram bot va AI agentlar

Qoidalar:
- Javoblarni o'zbek tilida ber.
- Avval amaliy yechimni ber.
- Kerak bo'lsa 1C 8.3 kodini yoz.
- Keraksiz nazariyani qisqartir.
- Screenshot yuborilsa, undagi 1C xatolik yoki oynani tahlil qil.
- Xatolik sababini va aniq tuzatish yo'lini bosqichma-bosqich tushuntir.
"""

async def send_long_message(update, text):
    max_length = 4000

    for i in range(0, len(text), max_length):
        await update.message.reply_text(
            text[i:i + max_length]
        )


# MATNLI SAVOL
async def text_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=f"{SYSTEM_PROMPT}\n\nFoydalanuvchi savoli:\n{text}"
    )

    await send_long_message(update, response.text)


# RASM
async def photo_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    photo = update.message.photo[-1]

    file = await context.bot.get_file(photo.file_id)

    image_bytes = await file.download_as_bytearray()

    user_text = update.message.caption or """
Bu rasm 1C:Enterprise dasturidan olingan.
Rasmni tahlil qil.
Agar xatolik bo'lsa:
1. Xatolik nima ekanini aniqlagin.
2. Sababini tushuntir.
3. Qanday tuzatishni bosqichma-bosqich ko'rsat.
4. Kerak bo'lsa 1C kodini ber.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[
            {
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": bytes(image_bytes)
                }
            },
            f"{SYSTEM_PROMPT}\n\n{user_text}"
        ]
    )

    await send_long_message(update, response.text)


app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# Matn
app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        text_reply
    )
)

# Rasm
app.add_handler(
    MessageHandler(
        filters.PHOTO,
        photo_reply
    )
)

print("1C AI Agent ishga tushdi...")

app.run_polling()