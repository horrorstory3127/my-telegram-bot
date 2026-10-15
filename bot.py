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
    await update.message.reply_text("Bot is working ✅\n/video horror story")

async def video(update, context):
    prompt = " ".join(context.args) or "horror"
    await update.message.reply_text(f"🎥 Dhoond raha hu: {prompt}")
    try:
        # Pixabay search
        api_url = f"https://pixabay.com/api/videos/?key={PIXABAY_KEY}&q={prompt}&per_page=3&safesearch=true"
        data = requests.get(api_url, timeout=20).json()

        if not data.get("hits"):
            await update.message.reply_text(f"Video nahi mila: {prompt}. Try: ghost, haunted house")
            return

        video_url = data["hits"][0]["videos"]["tiny"]["url"] # tiny is faster
        await update.message.reply_text("📥 Video download kar raha hu...")

        # Download video locally then upload to Telegram
        r = requests.get(video_url, timeout=60)
        with open("/tmp/video.mp4", "wb") as f:
            f.write(r.content)

        await update.message.reply_video(video=open("/tmp/video.mp4", "rb"), caption=f"{prompt} 👻")

    except Exception as e:
        await update.message.reply_text(f"Error: {e}\n\nCheck: Render > Environment me PIXABAY_API_KEY hai kya?")

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("video", video))
    app.run_polling()
