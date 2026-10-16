import os, requests, threading, asyncio, textwrap, time
from flask import Flask
from gtts import gTTS
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
from PIL import Image
# Compatibility fix for Pillow 10+
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS
from io import BytesIO

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY") # Optional hai, nahi bhi hoga to chalega
PORT = int(os.environ.get("PORT", 10000))

flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "Bot Live - Send /video <title>"

# --- STORY GENERATOR ---
def get_scenes_from_title(title):
    # Agar OpenAI key hai to real story, nahi to template
    if OPENAI_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_KEY)
            prompt = f"Write a 5-scene horror story in Hindi for title '{title}'. Each scene 1 line, scary, simple Hindi. Number them 1 to 5."
            res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"user","content":prompt}])
            text = res.choices[0].message.content
            scenes = [line.split(".",1)[-1].strip() for line in text.split("\n") if len(line.strip())>10][:5]
            if len(scenes)>=3: return scenes
        except Exception as e:
            print("OpenAI fail:", e)

    # Fallback template - kisi bhi title pe kaam karega
    t = title
    return [
        f"Ek chhote se gaon me {t} naam ki ek jagah thi jahan raat ko koi nahi jata tha.",
        f"Amit ne socha {t} ki sachchai kya hai, aur woh raat ko wahan chala gaya.",
        f"Wahan usne dekha ek budhi aurat khaali thaali liye baithi thi aur uski aankhein safed thi.",
        f"Jaise hi Amit ne thaali ko chua, poore kamre ki roshni bujh gayi aur darwaze band ho gaye.",
        f"Agli subah logon ko sirf ek khaali thaali mili, aur {t} ka raaz aaj bhi unsuljha hai."
    ]

def create_video(title, scenes):
    clips = []
    temp_files = []
    for i, scene_text in enumerate(scenes):
        print(f"Scene {i+1}: {scene_text}")
        # 1. Image
        img_url = f"https://image.pollinations.ai/prompt/horror cartoon style, dark night, {title}, {scene_text[:60]}, cinematic?width=1280&height=720&nologo=true&seed={i}{int(time.time())%100}"
        img_data = requests.get(img_url, timeout=60).content
        img_path = f"scene_{i}.jpg"
        Image.open(BytesIO(img_data)).save(img_path)

        # 2. Voice
        audio_path = f"scene_{i}.mp3"
        tts = gTTS(text=scene_text, lang='hi', slow=False)
        tts.save(audio_path)

        # 3. Clip
        audio_clip = AudioFileClip(audio_path)
        image_clip = ImageClip(img_path).set_duration(audio_clip.duration).set_audio(audio_clip)
        image_clip = image_clip.resize((1280, 720))
        clips.append(image_clip)
        temp_files.extend([img_path, audio_path])

    final_video = concatenate_videoclips(clips, method="compose")
    final_path = f"{title.replace(' ','_')}_final.mp4"
    final_video.write_videofile(final_path, fps=24, codec='libx264', audio_codec='aac')

    # cleanup clips only
    for f in temp_files:
        if os.path.exists(f): os.remove(f)
    return final_path

# --- TELEGRAM HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot Ready!\nBhej: /video <koi bhi title>\nEx: /video Bhoot Bangla")

async def video_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Title de bhai. Ex: /video Chauthi Thaali")
        return
    title = " ".join(context.args)
    await update.message.reply_text(f"🎬 Title: {title}\n⏳ 1-2 min ka video bana raha hu... (thoda time lagega)")

    try:
        scenes = get_scenes_from_title(title)
        video_path = await asyncio.to_thread(create_video, title, scenes)
        await update.message.reply_video(video=open(video_path,'rb'), caption=f"🎥 {title}\n\n" + "\n".join(scenes))
        if os.path.exists(video_path): os.remove(video_path)
    except Exception as e:
        print(e)
        await update.message.reply_text(f"Error aaya: {e}")

def run_telegram():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("video", video_cmd))
    print("Telegram Bot Started")
    app.run_polling()

if __name__ == "__main__":
    threading.Thread(target=lambda: flask_app.run(host="0.0.0.0", port=PORT), daemon=True).start()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    run_telegram()
