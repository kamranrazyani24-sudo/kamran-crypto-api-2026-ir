import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from server.data_fetcher import fetch_ohlcv
from server.patterns import find_patterns

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
    chat_id = update.message.chat_id
    
    # ارسال پیام "درحال پردازش" برای تجربه کاربری بهتر
    processing_msg = await update.message.reply_text(f"⏳ در حال دریافت داده‌های {symbol} و تحلیل الگوها...")

    try:
        # ۱. دریافت داده‌ها از بایننس
        df = fetch_ohlcv(f"{symbol}/USDT")
        
        if df is None or df.empty:
            await processing_msg.edit_text(f"❌ متاسفانه نتونستم داده‌های {symbol} رو دریافت کنم. مطمئنی نماد رو درست وارد کردی؟")
            return

        # ۲. شناسایی الگوها
        patterns = find_patterns(df)
        
        if not patterns:
            response = f"✅ تحلیل {symbol}:\n\nدر حال حاضر الگوی خاصی در نمودار دیده نمی‌شود."
        else:
            response = f"🚀 تحلیل {symbol}:\n\nالگوهای شناسایی شده:\n"
            for p in patterns:
                response += f"🔹 {p}\n"
        
        # ۳. ارسال پاسخ نهایی
        await processing_msg.edit_text(response)

    except Exception as e:
        print(f"Error: {e}")
        await processing_msg.edit_text("❌ متاسفانه در فرآیند تحلیل مشکلی پیش اومد. لطفاً دوباره تلاش کن.")
