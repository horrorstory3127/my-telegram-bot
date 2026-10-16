import os
import threading
import asyncio
import requests
import tempfile
from flask import Flask
from gtts import gTTS
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

BOT_TOKEN = os.environ.get("BOT_TOKEN")
PEXELS_KEY = os.environ.get("PEXELS_KEY")

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def get_images(query, n=3):
    try:
        if not PEXELS_KEY:
            print("PEXELS_KEY is missing!")
            raise Exception("No Key")
        headers = {"Authorization": PEXELS_KEY}
        url = f"https://api.pexels.com/v1/search?query={query}&per_page={n}&orientation=landscape"
        r = requests.get(url, headers=headers, timeout=15)
        data = r.json()
        photos = data.get('photos', [])
        if not photos:
            print(f"Pexels Empty: {data}")
            return [
                "https://images.pexels.com/photos/417173/pexels-photo-417173.jpeg",
                "https://images.pexels.com/photos/1366919/pexels-photo-1366919.jpeg"
            ]
        urls = [p["src"]["large"] for p in photos if "src" in p]
        return urls
    except Exception as e:
        print(f"get_images failed: {e}")
        return [
            "https://images.pexels.com/photos/417173/pexels-photo-417173.jpeg",
            "https://images.pexels.com/photos/1366919/pexels-photo-1366919.jpeg"
        ]

def download_image(url, path):
    # Ye header lagane se 403 Forbidden nahi ayega
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()
    with open(path, 'wb') as f:
        f.write(r.content)

def create_video(text, image_urls):
    tmpdir = tempfile.mkdtemp()
    audio_path = os.path.join(tmpdir, "voice.mp3")
    
    tts = gTTS(text=text, lang='hi', slow=False)
    tts.save(audio_path)
    
    audio_clip = AudioFileClip(audio_path)
    duration_per_img = audio_clip.duration / len(image_urls)
    
    clips = []
    for i, url in enumerate(image_urls):
        img_path = os.path.join(tmpdir, f"img{i}.jpg")
        download_image(url, img_path)
        clip = ImageClip(img_path, duration=duration_per_img)
        clip = clip.resize((1080, 1920)).set_position("center")
        clips.append(clip)
    
    final_video = concatenate_videoclips(clips, method="compose")
    final_video = final_video.set_audio(audio_clip)
    
    output_path = os.path.join(tmpdir, "final.mp4")
    final_video.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac')
    return output_path

# --- Telegram Handlers ---
async def start(update, context):
    await update.message.reply_text("Bhai script bhejo, video bana dunga! Gagan style me.")

async def handle_message(update, context):
    text = update.message.text
    if not text or text.startswith('/'):
        return
    await update.message.reply_text("Video bana raha hu...")
    try:
        # Simple keyword for image search
        query = "jungle night horror" if "jungle" in text or "haveli" in text else "mysterious landscape"
        images = get_images(query, n=3)
        video_path = await asyncio.to_thread(create_video, text, images)
        await update.message.reply_video(video=open(video_path, 'rb'))
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
        print(f"Video Error: {e}")

def run_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
