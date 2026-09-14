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

def get_chatgpt_response(prompt):
    """ Pollinations Text API for Free ChatGPT-like Chat """
    try:
        url = f"https://text.pollinations.ai/{requests.utils.quote(prompt)}?model=openai"
        res = requests.get(url, timeout=15)
        if res.status_code == 200:
            return res.text
    except Exception as e:
        print("Chat Error:", e)
    return "معذرت، اس وقت AI سرور میں کوئی مسئلہ ہے۔ دوبارہ کوشش کریں۔"

@app.route('/', methods=['GET'])
def index():
    return "ChatGPT + AI Image Bot is Online!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(force=True, silent=True)
    if not data or "message" not in data:
        return jsonify({"status": "ok"}), 200

    msg = data["message"]
    chat_id = msg["chat"]["id"]

    # 1. Photo Prompt (Image Editing)
    if "photo" in msg:
        caption = msg.get("caption", "hd high quality anime style")
        send_message(chat_id, f"🎨 تصویر ایڈٹ کی جا رہی ہے...")
        
        file_id = msg["photo"][-1]["file_id"]
        file_info = requests.get(f"{TELEGRAM_API}/getFile?file_id={file_id}").json()
        if file_info.get("ok"):
            file_path = file_info["result"]["file_path"]
            user_img_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
            
            edited_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(caption)}?image={requests.utils.quote(user_img_url)}&width=1024&height=1024&nologo=true"
            send_photo(chat_id, edited_url, caption=f"✨ Edited: {caption}")

    # 2. Text Prompts (ChatGPT Chat + Commands)
    elif "text" in msg:
        text = msg["text"].strip()

        if text == "/start":
            welcome = ("سلام! میں آپ کا **ChatGPT AI اسسٹنٹ** ہوں 🤖\n\n"
                       "💬 **Chat Mode:** آپ مجھ سے اردو یا انگریزی میں کوئی بھی سوال پوچھ سکتے ہیں، میں ChatGPT کی طرح جواب دوں گا۔\n\n"
                       "🖼️ **Image Creation:** اگر تصویر بنوانی ہو تو لکھیں: `/image a cat on moon`\n"
                       "🎥 **Video Creation:** اگر ویڈیو بنوانی ہو تو لکھیں: `/video a running horse`\n"
                       "🎨 **Image Editing:** تصویر بھیجیں اور کیپشن میں لکھیں کہ کیا بدلنا ہے۔")
            send_message(chat_id, welcome)

        elif text.lower().startswith("/image "):
            prompt = text[7:].strip()
            send_message(chat_id, f"🎨 تصویر بن رہی ہے: {prompt}...")
            img_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=1024&height=1024&nologo=true"
            send_photo(chat_id, img_url, caption=f"🖼️ {prompt}")

        elif text.lower().startswith("/video "):
            prompt = text[7:].strip()
            send_message(chat_id, f"🎬 ویڈیو بن رہی ہے: {prompt}...")
            video_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=512&height=512&nologo=true&model=turbo"
            requests.post(f"{TELEGRAM_API}/sendAnimation", json={"chat_id": chat_id, "animation": video_url, "caption": f"🎥 {prompt}"})

        else:
            # ChatGPT Direct Chat Reply
            response = get_chatgpt_response(text)
            send_message(chat_id, response)

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
