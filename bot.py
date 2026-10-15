import os, requests, threading
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from flask import Flask
from gtts import gTTS
from PIL import Image
from io import BytesIO

BOT_TOKEN = os.getenv("BOT_TOKEN")

def generate_story(prompt):
    if "cartoon" in prompt.lower():
        return f"Ek samay ki baat hai, {prompt} me ek chota sher tha. Wo bahut darpok tha. Ek din usne himmat dikhai aur jungle ka raja ban gaya."
    else:
        return f"Raat ke 2 baje, {prompt}. Ek ladka sunsan haveli me gaya. Darwaza khud band ho gaya. Piche se kisi ne hasne ki awaz aayi. Jab usne peeche dekha toh... waha ek safed saree wali chudail khadi thi!"

async def start(update, context):
    await update.message.reply_text("✅ Bot Ready! /video horror story likh")

async def video(update, context):
    prompt = " ".join(context.args) or "horror story"
    await update.message.reply_text(f"🎬 Bana raha hu: {prompt}...")

    try:
        story = generate_story(prompt)
        # 1. Voice
        audio_path = "/tmp/voice.mp3"
        gTTS(text=story, lang='hi').save(audio_path)
        
        # 2. Image (AI se)
        style = "cute cartoon" if "cartoon" in prompt.lower() else "horror, dark, cinematic, ultra realistic"
        img_url = f"https://image.pollinations.ai/prompt/{prompt} {style}"
        r = requests.get(img_url, timeout=30)
        img_path = "/tmp/thumb.jpg"
        Image.open(BytesIO(r.content)).save(img_path)

        # 3. Bhej de - YT ke liye Photo + Voice + Story
        await update.message.reply_photo(photo=open(img_path,"rb"), caption=f"{story}\n\n#horror #story")
        await update.message.reply_audio(audio=open(audio_path,"rb"), caption="Voiceover")
        await update.message.reply_text("Abhi Photo+Voice bhej raha hu, ye wala 100% chalega. Isko YT pe daalne ke liye bas InShot me jod de - full video ban jayega. Agla step me auto-video jod denge.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

flask_app = Flask(__name__)
@flask_app.route('/') 
def home(): return "OK"

def run_flask():
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("video", video))
    app.run_polling()
