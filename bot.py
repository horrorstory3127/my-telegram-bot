import os, requests, random
from moviepy.editor import *
from gtts import gTTS
from PIL import Image, ImageFilter

PEXELS_KEY = os.getenv("PEXELS_KEY")

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
    # 1. TTS
    tts = gTTS(text=script_text, lang='hi', slow=False)
    audio_path = "/tmp/audio.mp3"
    tts.save(audio_path)
    audio = AudioFileClip(audio_path)
    total_duration = audio.duration
    
    # 2. Images
    query = "dark motivational gym alone hustle"
    img_paths = get_images(query, 5)
    
    clips = []
    dur_each = total_duration / len(img_paths)
    
    for img_path in img_paths:
        img_clip = ImageClip(img_path).set_duration(dur_each)
        # Ken Burns zoom
        w,h = img_clip.size
        img_clip = img_clip.resize(height=1080).set_position('center').resize(lambda t: 1 + 0.08*t)
        clips.append(img_clip)

    final_video = concatenate_videoclips(clips, method="compose")
    final_video = final_video.set_audio(audio).set_duration(total_duration)
    final_video = final_video.resize(height=1920).crop(width=1080, height=1920, x_center=540, y_center=960)
    
    final_video.write_videofile(output, fps=24, codec='libx264', audio_codec='aac')
    return output
