import os
import requests
import threading
import asyncio
import time
from flask import Flask
from gtts import gTTS
from PIL import Image
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

from io import BytesIO
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")

# --- Flask keep alive ---
flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "Bot Running - Advance Version"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port)

# --- ADVANCE IMAGE (No API Key, No Error) ---
def get_image(prompt):
    try:
        q = requests.utils.quote(prompt + ", cinematic horror, 8k")
        url = f"https://image.pollinations.ai/prompt/{q}?width=1280&height=720&nologo=true&seed={int(time.time()*1000)%9999}"
        r = requests.get(url, timeout=60)
        if r.status_code == 200 and len(r.content) > 15000:
            bio = BytesIO(r.content)
            Image.open(bio).verify()
            bio.seek(0)
            return bio
    except: pass
    # Final fallback - never fails
    img = Image.new('RGB', (1280,720), color=(10,10,10))
    bio = BytesIO()
    img.save(bio, format='JPEG')
    bio.seek(0)
    return bio

def create_scenes(title):
    return [
        f"haunted well {title}, foggy night, horror",
        f"ghost woman near {title}, scary",
        f"man with torch near {title}, suspense",
        f"inside {title}, dark water, screaming",
        f"morning after {title}, village shocked"
    ]

async def video_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Bhej: /video chudail ka kuan")
        return
    title = " ".join(context.args)
    await update.message.reply_text(f"🎬 {title}\n⏳ 2 min me video bana raha hu...")

    try:
        scenes = create_scenes(title)
        clips = []
        files = []
        loop = asyncio.get_running_loop()

        for i, p in enumerate(scenes):
            img_bio = await loop.run_in_executor(None, get_image, p)
            pil = Image.open(img_bio).convert("RGB")
            img_path = f"/tmp/s_{i}.jpg"
            pil.save(img_path)

            tts = gTTS(text=p, lang='hi', slow=False)
            aud_path = f"/tmp/s_{i}.mp3"
            tts.save(aud_path)

            audio = AudioFileClip(aud_path)
            clip = ImageClip(img_path, duration=audio.duration+0.5).set_audio(audio).resize(height=720)
            clips.append(clip)
            files += [img_path, aud_path]

        final = concatenate_videoclips(clips, method="compose")
        out = f"/tmp/f_{int(time.time())}.mp4"
        final.write_videofile(out, fps=24, codec='libx264', audio_codec='aac', logger=None)

        await update.message.reply_video(video=open(out,'rb'), caption=title)

        for f in files+[out]:
            if os.path.exists(f): os.remove(f)
    except Exception as e:
        print(f"FINAL ERROR: {e}")
        await update.message.reply_text(f"Error: {e}")

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ready! Bhej /video chudail ka kuan")

# --- MAIN - NO EVENT LOOP ERROR ---
if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    # Yeh line sabse important hai - isse tera ab wala error khatam hoga
    try:
        asyncio.set_event_loop(asyncio.new_event_loop())
    except: pass

    print("Starting Advance Bot...")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("video", video_cmd))
    app.run_polling(drop_pending_updates=True)
