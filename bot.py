import os
import telebot
from telebot.types import LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton
from yt_dlp import YoutubeDL

TOKEN = "9131393110:AAFtQyfTYWNABrJYiMvvBCSVx-XXYhERYdg"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "مرحباً بك! 🤖\n"
        "أنا بوت تحميل الفيديوهات. صيفط لي أي رابط (يوتيوب، تيك توك، إنستغرام...) وسأتحمله لك.\n\n"
        "💡 إذا عجبك البوت وبغيتي تدعمني، تقدر تصيفط لي نجوم عبر الأمر: /donate"
    )
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⭐ ادعم البوت بالنجوم", callback_data="donate_stars"))
    bot.reply_to(message, welcome_text, reply_markup=markup)

@bot.message_handler(commands=['donate'])
def donate_command(message):
    send_invoice_stars(message.chat.id)

def send_invoice_stars(chat_id):
    title = "دعم صانع البوت ⭐"
    description = "شكراً لك على دعمك لاستمرار وتطوير البوت وتحسين الخدمات!"
    payload = "support-bot-stars"
    currency = "XTR"
    prices = [LabeledPrice(label="دعم بـ 50 نجمة", amount=50)]
    bot.send_invoice(
        chat_id=chat_id,
        title=title,
        description=description,
        invoice_payload=payload,
        provider_token="",
        currency=currency,
        prices=prices,
        start_parameter="donate-star",
        photo_url="https://images.unsplash.com/photo-1579783902614-a3fb3927b675?w=500",
        photo_height=512,
        photo_width=512
    )

@bot.callback_query_handler(func=lambda call: call.data == "donate_stars")
def callback_donate(call):
    bot.answer_callback_query(call.id)
    send_invoice_stars(call.message.chat.id)

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    payment_info = message.successful_payment
    bot.reply_to(message, f"❤️ الله يرحم الوالدين! توصلت بالدعم ديالك بنجاح ({payment_info.total_amount} نجمة). شكراً لك بزاف على تشجيعك!")

@bot.message_handler(func=lambda message: True)
def download_video(message):
    url = message.text.strip()
    if not url.startswith("http"):
        bot.reply_to(message, "عافاك صيفط رابط صحيح يبدأ بـ http أو https، ولا صيفط /donate إلا بغيتي تدعم البوت ⭐.")
        return

    msg = bot.reply_to(message, "⏳ جاري المعالجة والتحميل، يرجى الانتظار...")
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'max_filesize': 50 * 1024 * 1024,
    }
    os.makedirs('downloads', exist_ok=True)
    filename = None

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        if os.path.exists(filename):
            bot.edit_message_text("📤 جاري إرسال الفيديو...", message.chat.id, msg.message_id)
            with open(filename, 'rb') as video:
                bot.send_video(message.chat.id, video, timeout=120)
            bot.delete_message(message.chat.id, msg.message_id)
        else:
            bot.edit_message_text("❌ لم يتم العثور على الملف المحمل.", message.chat.id, msg.message_id)

    except Exception as e:
        error_msg = str(e)
        if "File is larger than max_filesize" in error_msg:
            bot.edit_message_text("❌ عذراً، حجم الفيديو كبير جداً (أكثر من 50 ميغا).", message.chat.id, msg.message_id)
        else:
            bot.edit_message_text(f"❌ حدث خطأ أثناء التحميل:\n{error_msg[:100]}", message.chat.id, msg.message_id)

    finally:
        if filename and os.path.exists(filename):
            try:
                os.remove(filename)
            except:
                pass

if __name__ == '__main__':
    print("Bot is up and running...")
    bot.infinity_polling()
