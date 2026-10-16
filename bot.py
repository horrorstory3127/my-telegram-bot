import os
import requests
import threading
import asyncio
import textwrap
import time
import re
from flask import Flask
from gtts import gTTS
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
from PIL import Image
# Compatibility fix for Pillow 10/11
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS
from io import BytesIO

# --- CONFIG ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
# Flask for Render keep-alive
app_flask = Flask(__name__)
@app_flask.route('/')
def home():
    return "Bot is Running!"

# --- FREE IMAGE GENERATOR (No API Key Needed) ---
def get_scene_image(prompt):
    try:
        safe_prompt = requests.utils.quote(prompt + ", cinematic horror, dark night, 8k, ultra detailed")
        url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1280&height=720&nologo=true&seed={int(time.time())%1000}"
        print(f"Downloading image: {prompt}")
        resp = requests.get(url, timeout=60)
        if resp.status_code == 200 and len(resp.content) > 10000:
            bio = BytesIO(resp.content)
            # Test if valid image
            Image.open(bio).verify()
            bio.seek(0)
            return bio
    except Exception as e:
        print(f"Image download failed: {e}")
    
    # Fallback black image
    print("Using fallback image")
    img = Image.new('RGB', (1280, 720), color=(15, 15, 15))
    bio = BytesIO()
    img.save(bio, format='JPEG')
    bio.seek(0)
    return bio

def create_story_scenes(title):
    # Simple story splitter - Gagan jaisa 5 scene
    title = title.strip()
    scenes = [
        f"a haunted well at midnight, foggy village, title {title}, horror cinematic",
        f"ghost of a woman near {title}, scary face, dark night",
        f"a man walking near {title} alone, holding torch light, suspense",
        f"inside {title}, dark water and screaming shadows, horror",
        f"morning after {title}, village people shocked, mysterious ending"
    ]
    return scenes

async def video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Use: /video chudail ka kuan")
        return
    
    title = " ".join(context.args)
    await update.message.reply_text(f"🎬 Title: {title}\n⏳ 1-2 min ka video bana raha hu...\n(thoda time lagega)")

    try:
        loop = asyncio.get_event_loop()
        scenes = create_story_scenes(title)
        
        clips = []
        temp_files = []

        for i, scene_prompt in enumerate(scenes):
            # 1. Image
            image_bio = await loop.run_in_executor(None, get_scene_image, scene_prompt)
            pil_img = Image.open(image_bio).convert("RGB")
            
            # Add text on image
            temp_img_path = f"/tmp/scene_{i}.jpg"
            pil_img.save(temp_img_path)
            
            # 2. Audio
            voice_text = f"Scene {i+1}. {scene_prompt}. " if i==0 else f"Aur phir. {scene_prompt}"
            tts = gTTS(text=voice_text, lang='hi', slow=False)
            temp_audio_path = f"/tmp/scene_{i}.mp3"
            tts.save(temp_audio_path)
            
            # 3. Video Clip
            audio_clip = AudioFileClip(temp_audio_path)
            img_clip = ImageClip(temp_img_path, duration=audio_clip.duration + 0.5)
            img_clip = img_clip.set_audio(audio_clip)
            img_clip = img_clip.resize(height=720)
            
            clips.append(img_clip)
            temp_files.extend([temp_img_path, temp_audio_path])

        # Final Video
        final_video = concatenate_videoclips(clips, method="compose")
        final_path = f"/tmp/{int(time.time())}.mp4"
        final_video.write_videofile(final_path, fps=24, codec='libx264', audio_codec='aac', logger=None)

        # Send
        await update.message.reply_video(video=open(final_path, 'rb'), caption=f"Ready: {title}")

        # Cleanup
        for f in temp_files + [final_path]:
            if os.path.exists(f):
                os.remove(f)
        for c in clips:
            c.close()

    except Exception as e:
        print(f"ERROR: {e}")
        await update.message.reply_text(f"Error aaya: {e}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bhoot wala bot ready hai! Bhej /video chudail ka kuan")

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    # Start Flask in background
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Start Telegram Bot
    print("Telegram Bot Started")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("video", video_command))
    app.run_polling()
