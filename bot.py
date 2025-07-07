import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters, ConversationHandler
)
from openpyxl import Workbook, load_workbook

TOKEN = os.environ.get("BOT_TOKEN") or "7723375117:AAF_mVLldYm-01G3r9A-26eV3GGnEg6-yEQ"
ADMIN_ID = int(os.environ.get("ADMIN_ID") or 6504169287)
EXCEL_FILE = "participants.xlsx"

LANG, NAME, SURNAME, SCHOOL, CLASS, ID_SERIES, PHOTO = range(7)
user_data = {}
user_langs = {}

MESSAGES = {
    "ru": {
        "name": "Введите ваше имя:",
        "surname": "Введите вашу фамилию:",
        "school": "Введите название вашей школы:",
        "class": "Введите ваш класс:",
        "id_series": "Введите номер и серию паспорта/ID-карты:",
        "payment": (
            "Переведите 100 000 сум на карту:\n"
            "`9860 0101 1633 2098` (HUMO)\n"
            "👤 Получатель: *Saidov Amirbek*\n\n"
            "📸 После оплаты отправьте сюда скриншот чека."
        ),
        "photo_sent": "Скриншот отправлен организатору. Ожидайте подтверждения.",
        "confirmed": "🎉 Ваша регистрация подтверждена! Удачи на олимпиаде.",
        "rejected": "❌ Регистрация отклонена. Пожалуйста, отправьте корректный чек ещё раз."
    },
    "uz": {
        "name": "Ismingizni kiriting:",
        "surname": "Familiyangizni kiriting:",
        "school": "Maktab nomini kiriting:",
        "class": "Sinfingizni kiriting:",
        "id_series": "Pasport/ID raqamingizni kiriting:",
        "payment": (
            "100 000 so'mni quyidagi kartaga o'tkazing:\n"
            "`9860 0101 1633 2098` (HUMO)\n"
            "👤 Qabul qiluvchi: *Saidov Amirbek*\n\n"
            "📸 To'lovdan so'ng check suratini yuboring."
        ),
        "photo_sent": "Check yuborildi. Tasdiqlanishini kuting.",
        "confirmed": "🎉 Ro'yxatdan o'tdingiz! Olimpiadada omad!",
        "rejected": "❌ Ro'yxatdan o'tish rad etildi. Iltimos, to'g'ri checkni yuboring."
    },
    "en": {
        "name": "Enter your first name:",
        "surname": "Enter your last name:",
        "school": "Enter your school name:",
        "class": "Enter your grade/class:",
        "id_series": "Enter your passport/ID number:",
        "payment": (
            "Please send 100,000 UZS to the card:\n"
            "`9860 0101 1633 2098` (HUMO)\n"
            "👤 Recipient: *Saidov Amirbek*\n\n"
            "📸 After payment, send the receipt screenshot here."
        ),
        "photo_sent": "Screenshot sent to the organizer. Please wait for confirmation.",
        "confirmed": "🎉 Registration confirmed! Good luck at the olympiad.",
        "rejected": "❌ Registration rejected. Please resend a valid receipt."
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang:ru")],
        [InlineKeyboardButton("🇺🇿 O'zbek", callback_data="lang:uz")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang:en")]
    ]
    await update.message.reply_text("🌐 Select a language:", reply_markup=InlineKeyboardMarkup(keyboard))
    return LANG

async def choose_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split(":")[1]
    uid = query.from_user.id
    user_langs[uid] = lang
    user_data[uid] = {}
    await query.message.reply_text(MESSAGES[lang]["name"])
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_data[uid]["name"] = update.message.text
    await update.message.reply_text(MESSAGES[user_langs[uid]]["surname"])
    return SURNAME

async def get_surname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_data[uid]["surname"] = update.message.text
    await update.message.reply_text(MESSAGES[user_langs[uid]]["school"])
    return SCHOOL

async def get_school(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_data[uid]["school"] = update.message.text
    await update.message.reply_text(MESSAGES[user_langs[uid]]["class"])
    return CLASS

async def get_class(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_data[uid]["class"] = update.message.text
    await update.message.reply_text(MESSAGES[user_langs[uid]]["id_series"])
    return ID_SERIES

async def get_id_series(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user = update.effective_user
    user_data[uid]["id_series"] = update.message.text
    user_data[uid]["tg_id"] = uid
    user_data[uid]["username"] = user.username or "без username"
    await update.message.reply_text(MESSAGES[user_langs[uid]]["payment"], parse_mode="Markdown")
    return PHOTO

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    data = user_data[uid]
    lang = user_langs[uid]
    photo = update.message.photo[-1].file_id
    caption = (
        f"🆕 Новая регистрация\n\n"
        f"👤 {data['name']} {data['surname']}\n"
        f"🏫 {data['school']}\n"
        f"📚 Класс: {data['class']}\n"
        f"🪪 ID: {data['id_series']}\n"
        f"🆔 @{data['username']} ({uid})"
    )
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Подтвердить", callback_data=f"approve:{uid}"),
            InlineKeyboardButton("❌ Отклонить", callback_data=f"reject:{uid}")
        ]
    ])
    await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo, caption=caption, reply_markup=keyboard)
    await update.message.reply_text(MESSAGES[lang]["photo_sent"])
    return ConversationHandler.END

async def confirm_participant(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = int(query.data.split(":")[1])
    if "approve" in query.data:
        save_to_excel(user_data[uid])
        await context.bot.send_message(chat_id=uid, text=MESSAGES[user_langs[uid]]["confirmed"])
        await query.edit_message_caption(query.message.caption + "\n\n✅ Подтверждено.")
        await context.bot.send_document(chat_id=ADMIN_ID, document=open(EXCEL_FILE, "rb"))
    else:
        await context.bot.send_message(chat_id=uid, text=MESSAGES[user_langs[uid]]["rejected"])
        await query.edit_message_caption(query.message.caption + "\n\n🚫 Отклонено.")

def save_to_excel(data):
    if not os.path.exists(EXCEL_FILE):
        wb = Workbook()
        ws = wb.active
        ws.append(["Имя", "Фамилия", "Школа", "Класс", "Серия и номер", "Telegram ID", "Username"])
    else:
        wb = load_workbook(EXCEL_FILE)
        ws = wb.active
    ws.append([data['name'], data['surname'], data['school'], data['class'], data['id_series'], data['tg_id'], data['username']])
    wb.save(EXCEL_FILE)

def main():
    app = Application.builder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANG: [CallbackQueryHandler(choose_lang, pattern="^lang:.*")],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            SURNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_surname)],
            SCHOOL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_school)],
            CLASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_class)],
            ID_SERIES: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_id_series)],
            PHOTO: [MessageHandler(filters.PHOTO, handle_photo)],
        },
        fallbacks=[],
    )
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(confirm_participant, pattern="^(approve|reject):"))
    print("Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    main()
