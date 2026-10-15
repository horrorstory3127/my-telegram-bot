import logging
import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
PIXABAY_KEY = os.getenv("PIXABAY_API_KEY")

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Hello {update.effective_user.first_name}! Bot is working ✅\n\n/video bhoot ki kahani - video ke liye")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Tune bola: {update.message.text}\nVideo ke liye /video likho")

async def video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("Bhai prompt to de! \nJaise: /video bhootiya haveli")
        return

    await update.message.reply_text(f"🎥 Video dhoond raha hu: '{prompt}'...")

    try:
        # Pixabay Video API
        url = f"https://pixabay.com/api/videos/?key={PIXABAY_KEY}&q={prompt}&per_page=3"
        r = requests.get(url, timeout=15)
        data = r.json()

        if data.get("hits"):
            video_url = data["hits"][0]["videos"]["medium"]["url"]
            await update.message.reply_video(video_url, caption=f"Ye le teri video: {prompt} 👻")
        else:
            await update.message.reply_text(f"Is prompt pe video nahi mila: {prompt}\nDusra prompt try kar jaise: horror, ghost, haunted house")

    except Exception as e:
        await update.message.reply_text(f"Error: {e}\nPIXABAY key check kar Koyeb me!")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("video", video))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    print("Bot chal raha hai...")
    app.run_polling()
