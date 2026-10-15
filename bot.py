import os, requests, threading
from flask import Flask
from gtts import gTTS
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

app_flask = Flask(__name__)
@app_flask.route('/')
def home():
    return "Bot Running!"

def generate_story(prompt):
    return f"""Ek raat ki baat hai, {prompt}...

Gaon ke log kehte the uss purane peepal ke ped ke neeche koi rehta hai. Raat ke 2 baje jab hawa chalti hai toh ek aurat ki siskari sunai deti hai.

Maine himmat karke wahan gaya. Wahan ek safed saree me ek aurat khadi thi, uske paair ulte the...

Usne dheere se kaha - "Tum bhi yahin rahoge..."

Uske baad kya hua, koi nahi janta."""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot Ready! /video horror chudail ki kahani")

async def video_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Likho: /video chudail ki kahani")
        return
    prompt = " ".join(context.args)
    await update.message.reply_text(f"⏳ Bana raha hu: {prompt}...")
    story = generate_story(prompt)
    try:
        img_url = f"https://image.pollinations.ai/prompt/horror%20scary%20{prompt}%20dark%20night%20cinematic?width=1080&height=1920&nologo=true"
        img_data = requests.get(img_url, timeout=30).content
        await update.message.reply_photo(photo=img_data, caption=story[:1000])
    except:
        await update.message.reply_text(story)
    try:
        tts = gTTS(text=story[:350], lang='hi', slow=False)
        tts.save("voice.mp3")
        await update.message.reply_voice(voice=open("voice.mp3","rb"))
    except:
        pass

def run_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("video", video_cmd))
    application.run_polling()

if __name__ == "__main__":
    threading.Thread(target=lambda: app_flask.run(host="0.0.0.0", port=10000)).start()
    run_bot()
