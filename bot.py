from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ConversationHandler, MessageHandler, filters, ContextTypes
)
from openpyxl import Workbook, load_workbook

TOKEN = "7723375117:AAF_mVLldYm-01G3r9A-26eV3GGnEg6-yEQ"  # <-- вставь сюда СВОЙ ТОКЕН

bot = Bot(token=TOKEN)
app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

LANGUAGE, MAIN_MENU = range(2)
ADMINS = [6504169287]  # <-- замените на свой Telegram user ID
user_data = {}

LANGUAGE_TEXTS = {
    "uz": "✅ Til tanlandi. Iltimos, /start buyrug'ini bosing.",
    "ru": "✅ Язык выбран. Пожалуйста, нажмите /start для начала.",
    "en": "✅ Language selected. Please press /start to begin."
}

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

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang_code = query.data.split("_")[1]
    user_id = query.from_user.id
    user_data[user_id] = {"lang": lang_code}
    await query.edit_message_text(LANGUAGE_TEXTS[lang_code])
    return MAIN_MENU

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in ADMINS:
        await update.message.reply_text("👮 Админ панель:\n/stat - Кол-во пользователей\n/deleteall - Очистить данные")
    else:
        await update.message.reply_text("⛔ У вас нет доступа.")

async def stat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in ADMINS:
        count = len(user_data)
        await update.message.reply_text(f"👥 Пользователей: {count}")

async def delete_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in ADMINS:
        user_data.clear()
        await update.message.reply_text("✅ Все данные удалены.")

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return "ok"

@app.route("/")
def index():
    return "Bot ishlayapti!"

def set_webhook():
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME') or 'olympiad-bot.onrender.com'}/{TOKEN}"
    application.bot.set_webhook(webhook_url)

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

if __name__ == '__main__':
    set_webhook()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
