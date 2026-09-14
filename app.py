import os
import requests
from flask import Flask, request
from telegram import Bot, Update

TOKEN = "8749846645:AAHj8ah8GhmNVLuGwD1_WWtaYfkyz3WcgsU"
bot = Bot(token=TOKEN)
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        try:
            data = request.get_json(force=True)
            if "message" in data:
                msg = data["message"]
                chat_id = msg["chat"]["id"]
                
                # 1. Image Edit Mode (Photo Upload)
                if "photo" in msg:
                    caption = msg.get("caption", "hd high quality anime style")
                    bot.send_message(chat_id=chat_id, text=f"🎨 تصویر ایڈٹ ہو رہی ہے ({caption})...")
                    
                    file_id = msg["photo"][-1]["file_id"]
                    file_info = requests.get(f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}").json()
                    file_path = file_info["result"]["file_path"]
                    user_img_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
                    
                    edited_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(caption)}?image={requests.utils.quote(user_img_url)}&width=1024&height=1024&nologo=true"
                    bot.send_photo(chat_id=chat_id, photo=edited_url, caption=f"✨ Edited: {caption}")
                    
                # 2. Text Prompts (Image & Video)
                elif "text" in msg:
                    text = msg["text"].strip()
                    
                    if text == "/start":
                        welcome = ("سلام! AI اسسٹنٹ بوٹ میں خوش آمدید:\n\n"
                                   "1️⃣ **تصویر کے لیے:** صرف ٹیکسٹ لکھیں (مثلاً: a lion in city)\n"
                                   "2️⃣ **ایڈٹ کے لیے:** فوٹو اپلوڈ کریں اور کیپشن میں لکھیں کیا بدلنا ہے\n"
                                   "3️⃣ **ویڈیو/اینیمیشن کے لیے:** شروع میں 'video' لکھیں (مثلاً: video a flying car)")
                        bot.send_message(chat_id=chat_id, text=welcome)
                        
                    elif text.lower().startswith("video "):
                        prompt = text[6:].strip()
                        bot.send_message(chat_id=chat_id, text=f"🎬 ویڈیو جنریٹ ہو رہی ہے: {prompt}...")
                        video_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=512&height=512&nologo=true&model=turbo"
                        bot.send_animation(chat_id=chat_id, animation=video_url, caption=f"🎥 Video: {prompt}")
                        
                    else:
                        bot.send_message(chat_id=chat_id, text=f"🎨 تصویر بنائی جا رہی ہے: {text}...")
                        img_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(text)}?width=1024&height=1024&nologo=true"
                        bot.send_photo(chat_id=chat_id, photo=img_url, caption=f"🖼️ Image: {text}")
        except Exception as e:
            print("Error:", e)
            
        return "ok"
    return "AI Bot Server Online!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
