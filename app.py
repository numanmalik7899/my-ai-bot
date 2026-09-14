import telebot
import requests

TOKEN = "8749846645:AAHj8ah8GhmNVLuGwD1_WWtaYfkyz3WcgsU"
bot = telebot.TeleBot(TOKEN)

# ChatGPT text chat
@bot.message_handler(func=lambda message: not message.text.startswith('/'))
def chat_reply(message):
    try:
        user_text = message.text
        url = f"https://text.pollinations.ai/{requests.utils.quote(user_text)}?model=openai"
        res = requests.get(url, timeout=20)
        if res.status_code == 200:
            bot.reply_to(message, res.text)
        else:
            bot.reply_to(message, "معذرت، اس وقت جواب دینے میں مسئلہ آ رہا ہے۔")
    except Exception as e:
        bot.reply_to(message, "سرور جواب نہیں دے رہا، دوبارہ کوشش کریں۔")

# Image Generator
@bot.message_handler(commands=['image'])
def image_reply(message):
    prompt = message.text.replace('/image', '').strip()
    if not prompt:
        bot.reply_to(message, "تصویر بنانے کے لیے کمانڈ ایسے لکھیں:\n`/image a beautiful cat`", parse_mode="Markdown")
        return
    
    bot.reply_to(message, f"🎨 تصویر بن رہی ہے: {prompt}...")
    img_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=1024&height=1024&nologo=true"
    bot.send_photo(message.chat.id, img_url, caption=f"🖼️ {prompt}")

# Start command
@bot.message_handler(commands=['start'])
def start_reply(message):
    bot.reply_to(message, "سلام! میں آپ کا AI اسسٹنٹ ہوں۔\n\n- آپ مجھ سے کچھ بھی پوچھیں، میں ChatGPT کی طرح جواب دوں گا۔\n- تصویر بنانے کے لیے لکھیں: `/image lion in space`")

bot.infinity_polling()
