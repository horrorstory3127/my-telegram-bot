import os
import threading
import requests, random
from flask import Flask
from gtts import gTTS
from PIL import Image, ImageFilter
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

def get_images(query, n=5):
    headers = {"Authorization": PEXELS_KEY}
    r = requests.get(f"https://api.pexels.com/v1/search?query={query}&per_page={n}&orientation=landscape", headers=headers, timeout=15)
    data = r.json()
    urls = [p['src']['large'] for p in data['photos']]
    paths = []
    for i, url in enumerate(urls):
        p = f"/tmp/{i}.jpg"
        open(p,'wb').write(requests.get(url, timeout=15).content)
        paths.append(p)
    return paths

def make_video(script_text, output="final.mp4"):
    tts = gTTS(text=script_text, lang='hi', slow=False)
    tts.save("/tmp/voice.mp3")
    # yaha tera bacha hua video logic ayega
    # simple ke liye image slideshow bana dete hain
    clips = [ImageClip(p).set_duration(2) for p in get_images(script_text, 3)]
    video = concatenate_videoclips(clips, method="compose")
    audioclip = AudioFileClip("/tmp/voice.mp3")
    video = video.set_audio(audioclip)
    video.write_videofile(output, fps=24)
    return output

async def start(update, context):
    await update.message.reply_text("Bhai video ke liye script bhejo!")

async def handle_text(update, context):
    script = update.message.text
    await update.message.reply_text("Video bana raha hu...")
    try:
        path = make_video(script)
        await update.message.reply_video(video=open(path,'rb'))
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("Bot chal raha hai...")
    application.run_polling()
