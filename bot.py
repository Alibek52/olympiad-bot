import os
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ConversationHandler, MessageHandler, filters, ContextTypes
)
from openpyxl import Workbook, load_workbook

# Этот токен будет из переменной окружения
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

# === Константы ===
LANGUAGE, MAIN_MENU = range(2)
ADMINS = [6504169287]  # Telegram ID админов

# === Языковые настройки ===
LANGUAGE_TEXTS = {
    "uz": "Илтимос, бослаш учун /start буюриғини босинг",
    "ru": "Пожалуйста, нажмите /start для начала",
    "en": "Please press /start to begin",
}

user_data = {}

# === Обработчик /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton("🇷🇺 Uzbek", callback_data="lang_uz"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
        ]
    ]
    await update.message.reply_text(
        "Тилни танланг / Choose language / Выберите язык",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return LANGUAGE

# === Обработчик языка ===
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang_code = query.data.split("_")[1]
    user_id = query.from_user.id
    user_data[user_id] = {"lang": lang_code}
    await query.edit_message_text(LANGUAGE_TEXTS[lang_code])
    return MAIN_MENU

# === Админ-панель ===
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in ADMINS:
        await update.message.reply_text("Админ панель: \n/stat - Статистика")
    else:
        await update.message.reply_text("У вас нет доступа")

# === Статистика ===
async def stat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in ADMINS:
        count = len(user_data)
        await update.message.reply_text(f"Общее число пользователей: {count}")

# === Фласк-сервер ===
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return "ok"

@app.route("/")
def index():
    return "Bot ishlayapti!"

# === Конверсация ===
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        LANGUAGE: [CallbackQueryHandler(set_language)],
    },
    fallbacks=[],
    per_user=True
)

# === Регистрация ===
application.add_handler(conv_handler)
application.add_handler(CommandHandler("admin", admin_panel))
application.add_handler(CommandHandler("stat", stat))

# === Запуск ===
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
