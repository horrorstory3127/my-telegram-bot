import logging
import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
# Agar Ikhdev API use karna hai to uska key Render me daalna padega
IKHDEV_API_URL = "https://api.ikhdev.com/generate-video" 

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Hello {update.effective_user.first_name}! Bot is working ✅\n\n/video bhoot ki kahani - video banane ke liye")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Tune bola: {update.message.text}\nVideo ke liye /video likho")

async def video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("Bhai prompt to de! \nJaise: /video ek bhootiya haveli")
        return

    await update.message.reply_text(f"⏳ Video bana raha hu: '{prompt}'...")

    # --- YAHAN TERA VIDEO API KA CODE AAYEGA ---
    # Abhi ke liye demo reply:
    # Agar tere paas Ikhdev API key hai to bata, main asli code daal dunga
    try:
        # Example: response = requests.post(IKHDEV_API_URL, json={"prompt": prompt})
        # video_url = response.json()['url']
        # await update.message.reply_video(video_url)
        await update.message.reply_text(f"✅ Video ka prompt mil gaya: {prompt}\n\nAb is prompt se video generate karne ke liye Ikhdev API ka key chahiye. API key hai tere paas?")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("video", video))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    print("Bot chal raha hai...")
    app.run_polling()
