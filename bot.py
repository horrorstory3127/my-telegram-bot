import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# Apna bot token yahan daal dena
BOT_TOKEN = "8877966729:AAHMZj-4B_Q-z8Zrav5VE2U9luhZoi3jomc"

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Hello {update.effective_user.first_name}! Bot is working ✅")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Tune bheja: {update.message.text}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    print("Bot chal raha hai...")
    app.run_polling()