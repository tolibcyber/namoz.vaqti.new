import logging
import os
import asyncio
import aiohttp
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()

TOKEN       = os.getenv("BOT_TOKEN")
ADMIN_ID    = int(os.getenv("ADMIN_ID", "7288739341"))
MINI_APP_URL = os.getenv("MINI_APP_URL", "https://namoz-vaqtlar.netlify.app")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

user_ids = set()

# Foydalanuvchi sozlamalari (eslatma vaqtlari)
user_settings = {}

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
    
    # Foydalanuvchini ro'yxatga olish
    if user.id not in user_settings:
        user_settings[user.id] = {
            "notify_before": 10,
            "enabled": True,
            "city": "Toshkent"
        }
    
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
# /setnotify - Eslatma vaqtini sozlash
# =============================================
async def set_notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text(
            "⚠️ *Ishlatilishi:* `/setnotify <daq_iqa>`\n\n"
            "Masalan:\n"
            "`/setnotify 5` - 5 daqiqa oldin eslatadi\n"
            "`/setnotify 10` - 10 daqiqa oldin eslatadi\n"
            "`/setnotify 15` - 15 daqiqa oldin eslatadi\n"
            "`/setnotify 20` - 20 daqiqa oldin eslatadi\n"
            "`/setnotify 30` - 30 daqiqa oldin eslatadi\n"
            "`/setnotify off` - Eslatmalarni o'chirish",
            parse_mode="Markdown"
        )
        return
    
    if context.args[0].lower() == "off":
        user_settings[user_id]["enabled"] = False
        await update.message.reply_text("❌ Namoz eslatmalari o'chirildi.")
        return
    
    try:
        minutes = int(context.args[0])
        if minutes not in [5, 10, 15, 20, 30]:
            await update.message.reply_text("❌ Faqat 5, 10, 15, 20 yoki 30 daqiqa qiymatlarini kiriting!")
            return
        
        user_settings[user_id]["notify_before"] = minutes
        user_settings[user_id]["enabled"] = True
        await update.message.reply_text(
            f"✅ Namoz eslatmalari yoqildi!\n"
            f"⏰ Har bir namozdan *{minutes} daqiqa oldin* xabar keladi.",
            parse_mode="Markdown"
        )
    except ValueError:
        await update.message.reply_text("❌ Iltimos, to'g'ri son kiriting!")

# =============================================
# /mycity - Shaharni sozlash
# =============================================
async def my_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text(
            "🏙️ *Shaharni sozlash*\n\n"
            "Ishlatilishi: `/mycity <shahar_nomi>`\n\n"
            "Masalan: `/mycity Toshkent`\n"
            "Qo'llab-quvvatlanadigan shaharlar:\n"
            "Toshkent, Samarqand, Buxoro, Farg'ona, Andijon, Namangan, Qo'qon, Nukus, Termiz, Qarshi, Navoiy, Jizzax",
            parse_mode="Markdown"
        )
        return
    
    city = " ".join(context.args)
    user_settings[user_id]["city"] = city
    await update.message.reply_text(f"✅ Shahringiz *{city}* ga o'zgartirildi!", parse_mode="Markdown")

# =============================================
# /status - Hozirgi sozlamalarni ko'rish
# =============================================
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    settings = user_settings.get(user_id, {"notify_before": 10, "enabled": True, "city": "Toshkent"})
    
    status_text = "🔔 *Eslatma sozlamalari*\n\n"
    status_text += f"🏙️ Shahar: *{settings.get('city', 'Toshkent')}*\n"
    status_text += f"⏰ Eslatma vaqti: *{settings.get('notify_before', 10)} daqiqa oldin*\n"
    status_text += f"📢 Holati: *{'✅ Yoqilgan' if settings.get('enabled', True) else '❌ O\'chirilgan'}*\n\n"
    status_text += "O'zgartirish uchun:\n"
    status_text += "▪️ `/setnotify 10` - vaqtni o'zgartirish\n"
    status_text += "▪️ `/mycity Toshkent` - shaharni o'zgartirish\n"
    status_text += "▪️ `/setnotify off` - eslatmalarni o'chirish"
    
    await update.message.reply_text(status_text, parse_mode="Markdown")

# =============================================
# NAMOZ VAQTLARINI API DAN OLISH
# =============================================
async def fetch_namoz_times(city):
    """namozvaqti.uz API dan namoz vaqtlarini olish"""
    try:
        url = f"https://namozvaqti.uz/api/prayer-times?city={city}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                if data.get("success") and data.get("times"):
                    return {
                        "Bomdod": data["times"]["bomdod"],
                        "Peshin": data["times"]["peshin"],
                        "Asr": data["times"]["asr"],
                        "Shom": data["times"]["shom"],
                        "Xufton": data["times"]["xufton"]
                    }
    except Exception as e:
        print(f"API xatosi: {e}")
    return None

# =============================================
# NAMOZ VAQTLARINI TEKSHIRISH (har daqiqada)
# =============================================
async def check_prayer_times(context: ContextTypes.DEFAULT_TYPE):
    """Har daqiqada ishlaydi va namoz vaqtlarini tekshiradi"""
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    
    for user_id, settings in user_settings.items():
        if not settings.get("enabled", True):
            continue
        
        city = settings.get("city", "Toshkent")
        notify_before = settings.get("notify_before", 10)
        
        # API dan namoz vaqtlarini olish (kesh bilan)
        cache_key = f"namoz_times_{city}"
        prayer_times = None
        
        # Keshni tekshirish (5 daqiqa)
        if hasattr(check_prayer_times, 'cache'):
            cached = check_prayer_times.cache.get(cache_key)
            if cached and (datetime.now() - cached['time']).seconds < 300:
                prayer_times = cached['times']
        
        if not prayer_times:
            prayer_times = await fetch_namoz_times(city)
            if prayer_times:
                if not hasattr(check_prayer_times, 'cache'):
                    check_prayer_times.cache = {}
                check_prayer_times.cache[cache_key] = {
                    'times': prayer_times,
                    'time': datetime.now()
                }
        
        if not prayer_times:
            continue
        
        for prayer_name, prayer_time in prayer_times.items():
            # Namoz vaqti kelganda
            if current_time == prayer_time:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"🕌 *{prayer_name}* namozining vaqti kirdi!\n\n📍 {city}\n⏰ {prayer_time}",
                    parse_mode="Markdown"
                )
            
            # Oldindan ogohlantirish
            prayer_dt = datetime.strptime(prayer_time, "%H:%M")
            notify_dt = prayer_dt - timedelta(minutes=notify_before)
            notify_time = notify_dt.strftime("%H:%M")
            
            if current_time == notify_time:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"⏰ *{notify_before} daqiqadan so'ng* {prayer_name} namozining vaqti kiradi!\n\n📍 {city}\n🕌 Tayyorlaning!",
                    parse_mode="Markdown"
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
        "📍 Namoz vaqtlari\n"
        "🧭 Qibla kompasi\n"
        "🌡️ Ob-havo\n"
        "📅 Hijriy taqvim\n"
        "🔔 Namoz eslatmalari\n\n"
        "👇 Mini App orqali:\n"
        "🌅 Bomdod, Peshin, Asr, Shom, Xufton\n"
        "⏰ Countdown taymer\n\n"
        "👨‍💻 @TolibDev",
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
    
    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CommandHandler("setnotify", set_notify))
    app.add_handler(CommandHandler("mycity", my_city))
    app.add_handler(CommandHandler("status", status))
    
    # Callback and message handlers
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Har daqiqada ishlaydigan job scheduler (eslatmalar uchun)
    job_queue = app.job_queue
    if job_queue:
        job_queue.run_repeating(check_prayer_times, interval=60, first=10)
    
    print("✅ Namoz Vaqtlari Bot ishga tushdi!")
    print("📢 Eslatmalar har daqiqada tekshiriladi!")
    app.run_polling()

if __name__ == "__main__":
    main()
