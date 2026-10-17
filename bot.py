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

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def get_images(query, n=3):
    # Bina API key ke free images
    return [
        "https://images.pexels.com/photos/417173/pexels-photo-417173.jpeg?auto=compress&cs=tinysrgb&w=720",
        "https://images.pexels.com/photos/1366919/pexels-photo-1366919.jpeg?auto=compress&cs=tinysrgb&w=720",
        "https://images.pexels.com/photos/3617500/pexels-photo-3617500.jpeg?auto=compress&cs=tinysrgb&w=720"
    ][:n]

def create_video(text):
    images = get_images(text)
    temp_dir = tempfile.mkdtemp()
    
    # Voice
    tts = gTTS(text=text[:500], lang='hi')
    audio_path = os.path.join(temp_dir, "audio.mp3")
    tts.save(audio_path)
    audio = AudioFileClip(audio_path)
    
    clips = []
    dur = audio.duration / len(images)
    for img_url in images:
        try:
            img_data = requests.get(img_url, timeout=10).content
            img_path = os.path.join(temp_dir, f"{len(clips)}.jpg")
            with open(img_path, 'wb') as f:
                f.write(img_data)
            clip = ImageClip(img_path).set_duration(dur).resize(height=720)
            clips.append(clip)
        except:
            continue
    
    if not clips:
        return None

    final = concatenate_videoclips(clips)
    final = final.set_audio(audio)
    out_path = os.path.join(temp_dir, "final.mp4")
    final.write_videofile(out_path, fps=24, codec='libx264', audio_codec='aac', verbose=False, logger=None)
    return out_path

async def start(update, context):
    await update.message.reply_text("Bhai koi bhi kahani bhej, mai video bana dunga!")

async def handle_msg(update, context):
    text = update.message.text
    await update.message.reply_text("Video bana raha hu... 30 sec ruk ja bhai ⏳")
    try:
        loop = asyncio.get_event_loop()
        video_path = await loop.run_in_executor(None, create_video, text)
        if video_path:
            await update.message.reply_video(video=open(video_path, 'rb'))
        else:
            await update.message.reply_text("Image download me error aaya, dusri kahani bhej.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

def run_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))
    application.run_polling()

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
