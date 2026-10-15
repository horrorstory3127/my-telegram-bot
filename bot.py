import os, threading, requests
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
PIXABAY_KEY = os.getenv("PIXABAY_API_KEY")

flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "Bot Live"

def run_flask():
    flask_app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

async def start(update, context):
    await update.message.reply_text("Hello Rohit! Bot is working ✅\n/video horror story likh video aayegi")

async def video(update, context):
    prompt = " ".join(context.args) or "horror"
    await update.message.reply_text(f"🎥 Dhoond raha hu: {prompt}")
    try:
        r = requests.get(f"https://pixabay.com/api/videos/?key={PIXABAY_KEY}&q={prompt}&per_page=3", timeout=20).json()
        if r.get("hits"):
            url = r["hits"][0]["videos"]["medium"]["url"]
            await update.message.reply_video(url, caption=f"{prompt} 👻")
        else:
            await update.message.reply_text("Video nahi mila, dusra naam try kar: ghost, haunted")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("video", video))
    app.run_polling()
