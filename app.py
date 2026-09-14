import os
import requests
from flask import Flask, request, jsonify

TOKEN = "8749846645:AAHj8ah8GhmNVLuGwD1_WWtaYfkyz3WcgsU"
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def send_photo(chat_id, photo_url, caption=""):
    url = f"{TELEGRAM_API}/sendPhoto"
    payload = {"chat_id": chat_id, "photo": photo_url, "caption": caption}
    requests.post(url, json=payload)

def send_animation(chat_id, anim_url, caption=""):
    url = f"{TELEGRAM_API}/sendAnimation"
    payload = {"chat_id": chat_id, "animation": anim_url, "caption": caption}
    requests.post(url, json=payload)

@app.route('/', methods=['GET'])
def index():
    return "AI Bot Server Online!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"status": "no data"}), 200

    if "message" in data:
        msg = data["message"]
        chat_id = msg["chat"]["id"]
        
        # 1. Image Edit Mode (Photo Upload)
        if "photo" in msg:
            caption = msg.get("caption", "hd high quality anime style")
            send_message(chat_id, f"🎨 تصویر ایڈٹ ہو رہی ہے ({caption})...")
            
            file_id = msg["photo"][-1]["file_id"]
            file_info = requests.get(f"{TELEGRAM_API}/getFile?file_id={file_id}").json()
            if file_info.get("ok"):
                file_path = file_info["result"]["file_path"]
                user_img_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
                
                edited_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(caption)}?image={requests.utils.quote(user_img_url)}&width=1024&height=1024&nologo=true"
                send_photo(chat_id, edited_url, caption=f"✨ Edited: {caption}")
            
        # 2. Text Prompts (Image & Video)
        elif "text" in msg:
            text = msg["text"].strip()
            
            if text == "/start":
                welcome = ("سلام! AI اسسٹنٹ بوٹ میں خوش آمدید:\n\n"
                           "1️⃣ **تصویر کے لیے:** صرف ٹیکسٹ لکھیں (مثلاً: a lion in city)\n"
                           "2️⃣ **ایڈٹ کے لیے:** فوٹو اپلوڈ کریں اور کیپشن میں لکھیں کیا بدلنا ہے\n"
                           "3️⃣ **ویڈیو/اینیمیشن کے لیے:** شروع میں 'video' لکھیں (مثلاً: video a flying car)")
                send_message(chat_id, welcome)
                
            elif text.lower().startswith("video "):
                prompt = text[6:].strip()
                send_message(chat_id, f"🎬 ویڈیو جنریٹ ہو رہی ہے: {prompt}...")
                video_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=512&height=512&nologo=true&model=turbo"
                send_animation(chat_id, video_url, caption=f"🎥 Video: {prompt}")
                
            else:
                send_message(chat_id, f"🎨 تصویر بنائی جا رہی ہے: {text}...")
                img_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(text)}?width=1024&height=1024&nologo=true"
                send_photo(chat_id, img_url, caption=f"🖼️ Image: {text}")

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
