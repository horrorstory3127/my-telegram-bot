import os
import threading
import asyncio
import requests
from flask import Flask
from gtts import gTTS
from moviepy.editor import *
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

BOT_TOKEN = os.environ.get("BOT_TOKEN")
PEXELS_KEY = os.getenv("PEXELS_KEY")

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def get_images(query, n=3):
    try:
        headers = {"Authorization": PEXELS_API_KEY}
        r = requests.get(f"https://api.pexels.com/v1/search?query={query}&per_page={n}&orientation=landscape", headers=headers, timeout=15)
        data = r.json()
        photos = data.get('photos', [])
        if not photos:
            print(f"Pexels Error/Empty: {data}")
            return []
        urls = [p["src"]["large"] for p in photos if "src" in p]
        return urls
    except Exception as e:
        print(f"get_images failed: {e}")
        return []
def make_video(script_text, output="/tmp/final.mp4"):
    tts = gTTS(text=script_text, lang='hi', slow=False)
    tts.save("/tmp/voice.mp3")
    clips = [ImageClip(p).set_duration(2) for p in get_images(script_text, 3)]
    video = concatenate_videoclips(clips, method="compose")
    audioclip = AudioFileClip("/tmp/voice.mp3")
    video = video.set_audio(audioclip)
    video.write_videofile(output, fps=24)
    return output

async def start(update, context):
    await update.message.reply_text("Bhai script bhejo, video bana dunga!")

async def handle_text(update, context):
    script = update.message.text
    await update.message.reply_text("Video bana raha hu...")
    try:
        path = make_video(script)
        await update.message.reply_video(video=open(path,'rb'))
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.run_polling(stop_signals=None)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    run_flask()
