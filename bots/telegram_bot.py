from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# این تابع را FastAPI صدا می‌زند
async def process_update(update_dict, token):
    application = ApplicationBuilder().token(token).build()
    # اینجا هندلرها را اضافه کن
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    update = Update.de_json(update_dict, application.bot)
    await application.initialize()
    await application.process_update(update)

async def start(update, context):
    await update.message.reply_text("ربات آماده است! یک نماد بفرست.")

async def handle_message(update, context):
    symbol = update.message.text.upper()
    await update.message.reply_text(f"تحلیل {symbol} انجام شد...")
