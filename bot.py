import os, threading, requests
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
PIXABAY_KEY = os.getenv("PIXABAY_API_KEY")

fa = Flask(__name__)
@fa.route('/')
def h(): return "Live"
def rf(): fa.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000)))

async def video(update, context):
    q = " ".join(context.args) or "horror"
    await update.message.reply_text(f"🎥 Dhoond raha hu: {q}")
    try:
        d = requests.get(f"https://pixabay.com/api/videos/?key={PIXABAY_KEY}&q={q}&per_page=3", timeout=20).json()
        if not d.get("hits"):
            await update.message.reply_text("Video nahi mila"); return
        vurl = d["hits"][0]["videos"]["tiny"]["url"]
        data = requests.get(vurl, timeout=60).content
        open("/tmp/v.mp4","wb").write(data)
        await update.message.reply_video(video=open("/tmp/v.mp4","rb"), caption=f"{q} 👻")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

if __name__ == "__main__":
    threading.Thread(target=rf, daemon=True).start()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("video", video))
    app.add_handler(CommandHandler("start", video))
    app.run_polling()
