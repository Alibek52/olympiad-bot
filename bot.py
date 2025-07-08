import os
import asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ConversationHandler, ContextTypes
)
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

# Состояния
LANGUAGE, MAIN_MENU = range(2)

# Админы
ADMINS = [6504169287]
user_data = {}

# Тексты по языкам
LANGUAGE_TEXTS = {
    "uz": "✅ Til tanlandi. Iltimos, /start buyrug'ini bosing.",
    "ru": "✅ Язык выбран. Пожалуйста, нажмите /start для начала.",
    "en": "✅ Language selected. Please press /start to begin."
}

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton("🇺🇿 O'zbek", callback_data="lang_uz"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
        ]
    ]
    await update.message.reply_text(
        "🌐 Выберите язык / Tilni tanlang / Choose a language:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return LANGUAGE

# Установка языка
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang_code = query.data.split("_")[1]
    user_id = query.from_user.id
    user_data[user_id] = {"lang": lang_code}
    await query.edit_message_text(LANGUAGE_TEXTS[lang_code])
    return MAIN_MENU

# /admin
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in ADMINS:
        await update.message.reply_text("👮 Админ панель:\n/stat - Кол-во пользователей\n/deleteall - Очистить данные")
    else:
        await update.message.reply_text("⛔ У вас нет доступа.")

# /stat
async def stat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in ADMINS:
        count = len(user_data)
        await update.message.reply_text(f"👥 Пользователей: {count}")

# /deleteall
async def delete_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in ADMINS:
        user_data.clear()
        await update.message.reply_text("✅ Все данные удалены.")

# Вебхук для Telegram
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return "ok"

# Корневая страница
@app.route("/")
def index():
    return "Bot ishlayapti!"

# Обработчики
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={LANGUAGE: [CallbackQueryHandler(set_language)]},
    fallbacks=[],
    per_user=True
)

application.add_handler(conv_handler)
application.add_handler(CommandHandler("admin", admin_panel))
application.add_handler(CommandHandler("stat", stat))
application.add_handler(CommandHandler("deleteall", delete_all))

# Запуск
if __name__ == '__main__':
    async def run():
        webhook_url = f"https://olympiad-bot.onrender.com/{TOKEN}"
        await application.bot.set_webhook(webhook_url)
        print(f"✅ Webhook set: {webhook_url}")

    asyncio.run(run())

    # Flask не даёт завершиться приложению
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
