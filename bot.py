import os
import requests
import threading
from flask import Flask
from gtts import gTTS
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 10000))

flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "Bot is Live!"

def get_story(prompt):
    return f"Ek raat ki baat hai, {prompt} ki kahani. Gaon ke log kehte the uss ped ke neeche koi rehta hai. Raat ke 2 baje ek safed saree wali aurat dikhti hai jiske paair ulte hote hai. Usne kaha - Tum bhi yahin rahoge..."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot Ready! Bhej: /video chudail ki kahani")

async def video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Ex: /video horror chudail")
        return
    prompt = " ".join(context.args)
    await update.message.reply_text(f"⏳ Bana raha hu: {prompt}")
    story = get_story(prompt)
    try:
        url = f"https://image.pollinations.ai/prompt/horror {prompt} dark scary cinematic?width=1080&height=1920&nologo=true"
        r = requests.get(url, timeout=30)
        await update.message.reply_photo(photo=r.content, caption=story)
    except Exception as e:
        await update.message.reply_text(story)
    try:
        tts = gTTS(text=story[:300], lang='hi')
        tts.save("v.mp3")
        await update.message.reply_voice(voice=open("v.mp3","rb"))
    except:
        pass

def run_telegram():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("video", video))
    print("Telegram Bot Started")
    app.run_polling()

if __name__ == "__main__":
    import asyncio
    # Fix for Render
    def run_flask():
        flask_app.run(host="0.0.0.0", port=PORT)
    
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Event loop fix - yahi error tha
    asyncio.set_event_loop(asyncio.new_event_loop())
    run_telegram()
