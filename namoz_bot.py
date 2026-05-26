import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()

TOKEN       = os.getenv("BOT_TOKEN")
ADMIN_ID    = int(os.getenv("ADMIN_ID", "7288739341"))
MINI_APP_URL = os.getenv("MINI_APP_URL", "https://your-domain.com")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

user_ids = set()


# =============================================
# KLAVIATURA
# =============================================
def get_start_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text="🕌 Namoz vaqtlarini ochish",
            web_app=WebAppInfo(url=MINI_APP_URL),
        )],
        [InlineKeyboardButton(
            text="ℹ️ Bot haqida",
            callback_data="about",
        )],
    ])


# =============================================
# /start
# =============================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_ids.add(user.id)
    first_name = user.first_name or "Foydalanuvchi"

    text = (
        f"☪️ *Assalomu alaykum, {first_name}!*\n\n"
        "🕌 *Namoz Vaqtlari* botiga xush kelibsiz!\n\n"
        "━━━━━━━━━━━━━━━\n"
        "📱 Mini App orqali:\n\n"
        "🌅  Bomdod, Peshin, Asr, Shom, Xufton vaqtlari\n"
        "⏰  Keyingi namozgacha countdown taymer\n"
        "🧭  Real vaqtda Qibla kompasi\n"
        "📅  Hijri taqvim\n"
        "━━━━━━━━━━━━━━━\n\n"
        "👇 Pastdagi tugmani bosing:"
    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_start_keyboard(),
    )


# =============================================
# CALLBACK: Bot haqida
# =============================================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    user_ids.add(user.id)

    if query.data == "about":
        await query.message.reply_text(
            "🕌 *Namoz Vaqtlari Bot*\n\n"
            "Bu bot Telegram Mini App orqali ishlaydi.\n\n"
            "📡 Ma'lumot manbai: *Aladhan API*\n"
            "🌍 8 ta mamlakat, 30+ shahar\n"
            "🔄 Vaqtlar har kuni yangilanadi\n"
            "💾 Oflayn kesh (1 soat)\n\n"
            "👨‍💻 Muallif: @TolibDev\n"
            "📌 Versiya: 2.0.0",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    "🕌 Mini Appni ochish",
                    web_app=WebAppInfo(url=MINI_APP_URL),
                )
            ]]),
        )

    # Admin
    elif query.data == "user_count":
        if user.id != ADMIN_ID:
            return
        await query.message.reply_text(
            f"👥 Jami foydalanuvchilar: *{len(user_ids)}* ta",
            parse_mode="Markdown",
        )

    elif query.data == "broadcast":
        if user.id != ADMIN_ID:
            return
        context.user_data["waiting_broadcast"] = True
        await query.message.reply_text(
            "✍️ Hammaga yubormoqchi bo'lgan xabaringizni yozing:\n_(Bekor qilish: /cancel)_",
            parse_mode="Markdown",
        )


# =============================================
# ADMIN PANEL
# =============================================
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Sizda ruxsat yo'q!")
        return

    await update.message.reply_text(
        f"⚙️ *Admin Panel*\n\n👥 Foydalanuvchilar: *{len(user_ids)}* ta",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👥 Foydalanuvchilar soni", callback_data="user_count")],
            [InlineKeyboardButton("📨 Hammaga xabar yuborish", callback_data="broadcast")],
        ]),
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["waiting_broadcast"] = False
    await update.message.reply_text("❌ Bekor qilindi.")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_ids.add(user.id)

    # Admin broadcast
    if user.id == ADMIN_ID and context.user_data.get("waiting_broadcast"):
        context.user_data["waiting_broadcast"] = False
        await update.message.reply_text(f"⏳ Yuborilmoqda... ({len(user_ids)} ta foydalanuvchi)")
        success, failed = 0, 0
        for uid in list(user_ids):
            try:
                await context.bot.send_message(chat_id=uid, text=update.message.text)
                success += 1
            except Exception:
                failed += 1
        await update.message.reply_text(
            f"✅ Yuborish yakunlandi!\n✔️ Muvaffaqiyatli: *{success}*\n❌ Xatolik: *{failed}*",
            parse_mode="Markdown",
        )
        return

    # Boshqa xabarlar uchun /start ga yo'naltirish
    await update.message.reply_text(
        "👇 Namoz vaqtlarini ko'rish uchun:",
        reply_markup=get_start_keyboard(),
    )


# =============================================
# MAIN
# =============================================
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start",  start))
    app.add_handler(CommandHandler("admin",  admin))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("✅ Namoz Vaqtlari Bot ishga tushdi!")
    app.run_polling()


if __name__ == "__main__":
    main()
