import os, textwrap, requests, tempfile
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from flask import Flask
import threading
from gtts import gTTS
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
from PIL import Image
from io import BytesIO

BOT_TOKEN = os.getenv("BOT_TOKEN")

# --- YT ke liye Story Generator ---
def generate_story(prompt):
    # Agar prompt me cartoon hai to cartoon story, nahi to horror
    if "cartoon" in prompt.lower():
        story = f"Ek samay ki baat hai, {prompt} ke jangal me ek chota bacha kho gaya. Usne himmat nahi hari aur ant me apne ghar wapas aa gaya. Moral: Himmat se sab hota hai."
    else:
        story = f"Raat ke 12 baje, {prompt}... Ek sunsan haveli me ek ladka akela tha. Achanak darwaza khud band ho gaya. Piche se kisi ne uska naam liya... Wo palta to waha koi nahi tha, bas ek parchai thi jo has rahi thi. Agli subah logon ko sirf uske cheekhne ki awaz yaad thi."
    # 4 scenes me tod de
    sentences = story.split(". ")
    return sentences[:4]

def create_yt_video(prompt, sentences):
    clips = []
    audio_clips = []
    temp_files = []
    
    for i, sentence in enumerate(sentences):
        # 1. Voiceover banao (gTTS free hai)
        tts = gTTS(text=sentence, lang='hi', slow=False)
        audio_path = f"/tmp/audio_{i}.mp3"
        tts.save(audio_path)
        audio = AudioFileClip(audio_path)
        
        # 2. Image banao (Pollinations AI - free, no API key)
        # Cartoon ya Horror ke hisab se style
        style = "cartoon style, cute" if "cartoon" in prompt.lower() else "horror style, dark, cinematic, 8k"
        img_prompt = f"{sentence}, {style}"
        img_url = f"https://image.pollinations.ai/prompt/{img_prompt}"
        try:
            r = requests.get(img_url, timeout=30)
            img = Image.open(BytesIO(r.content)).resize((1280,720))
            img_path = f"/tmp/img_{i}.jpg"
            img.save(img_path)
        except:
            # agar fail to black image
            img_path = f"/tmp/img_{i}.jpg"
            Image.new('RGB', (1280,720), color='black').save(img_path)

        # 3. Image + Audio = Video Clip
        img_clip = ImageClip(img_path).set_duration(audio.duration + 0.5).set_audio(audio)
        clips.append(img_clip)
        temp_files.append(audio_path)
        temp_files.append(img_path)

    # Sab clips jodo
    final_video = concatenate_videoclips(clips, method="compose")
    output_path = "/tmp/final_yt_video.mp4"
    final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
    return output_path

# --- Telegram Commands ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot Ready!\n/video horror story - ke liye\n/video cartoon story - ke liye")

async def video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args) or "horror story"
    await update.message.reply_text(f"🎬 Bana raha hu: {prompt}\nThoda time lagega (40 sec)...")

    try:
        sentences = generate_story(prompt)
        video_path = create_yt_video(prompt, sentences)
        
        caption = ". ".join(sentences)
        await update.message.reply_video(video=open(video_path, "rb"), caption=f"YT Ready Video: {prompt}\n\n{caption}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# --- Flask for Render ---
flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "Bot Running - YT Mode"

def run_flask():
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("video", video))
    app.run_polling()
