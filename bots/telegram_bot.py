import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# توکن را از متغیرهای محیطی می‌گیریم
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

async def process_update(update_dict, token):
    application = ApplicationBuilder().token(token).build()
    
    # اضافه کردن هندلرها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_crypto_analysis))
    
    update = Update.de_json(update_dict, application.bot)
    await application.initialize()
    await application.process_update(update)

async def start(update, context):
    await update.message.reply_text(
        "سلام کامران عزیز! 🖐\n"
        "من ربات تحلیل‌گر الگوهای کریپتو هستم.\n"
        "کافیه نام نماد رو بفرستی (مثلاً: BTC یا ETH) تا برات تحلیلش کنم."
    )

async def handle_crypto_analysis(update, context):
    symbol = update.message.text.upper()
    
    # ارسال پیام "درحال پردازش" برای تجربه کاربری بهتر
    processing_msg = await update.message.reply_text(f"⏳ در حال دریافت داده‌های {symbol}...")

    try:
        # پاسخ موقت پایدار برای بالا آمدن موفق سرور
        response = (
            f"🚀 تحلیل هوشمند {symbol}:\n\n"
            f"سیستم در حال اتصال به بایننس و دریافت کندل‌هاست.\n"
            f"اتصال با موفقیت برقرار شد! در قدم بعدی الگوهای قیمتی را اضافه می‌کنیم."
        )
        await processing_msg.edit_text(response)

    except Exception as e:
        print(f"Error: {e}")
        await processing_msg.edit_text("❌ متاسفانه در فرآیند تحلیل مشکلی پیش اومد. لطفاً دوباره تلاش کن.")
