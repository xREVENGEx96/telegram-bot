import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import os
import yt_dlp
from keep_alive import keep_alive
keep_alive()
from flask import Flask
import threading

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot attivo e funzionante!"

def start_flask():
    app.run(host="0.0.0.0", port=8080)

# Avvia Flask in un thread separato
threading.Thread(target=start_flask).start()



TOKEN = "7546015886:AAHwDclDMO0g8EMZm41ltzezqJZrxDSVZkM"
bot = telebot.TeleBot(TOKEN)

DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def download_video(url, chat_id, format_type):
    bot.send_message(chat_id, "🎥 Download in corso, attendi...")

    options = {
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'merge_output_format': 'mp4',  # Forza MP4
    }

    if format_type == "mp3":
        options.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
        ext = ".mp3"
    elif format_type == "mp4":
        options.update({
            'format': 'bestvideo[height<=720]+bestaudio/best',  # Limita la qualità a 720p o meno
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }]
        })
        ext = ".mp4"

    with yt_dlp.YoutubeDL(options) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            file_base = info['title']
            file_name = f"{DOWNLOAD_FOLDER}/{file_base}{ext}"

            for file in os.listdir(DOWNLOAD_FOLDER):
                if file.startswith(file_base):
                    file_name = f"{DOWNLOAD_FOLDER}/{file}"
                    break

            if os.path.exists(file_name):
                file_size = os.path.getsize(file_name) / (1024 * 1024)  

                if file_size > 50:
                    bot.send_message(chat_id, f"❌ Il file è troppo grande ({file_size:.2f}MB).")
                else:
                    with open(file_name, "rb") as file:
                        if format_type == "mp3":
                            bot.send_audio(chat_id, file)
                        else:
                            bot.send_video(chat_id, file)

                os.remove(file_name)  
                bot.send_message(chat_id, "✅ Download completato! E si pigghiu a mamma i cu fuuuuuu, ciuuuu nfiluuuu")
            else:
                bot.send_message(chat_id, "❌ Errore: il file non è stato trovato!")

        except Exception as e:
            bot.send_message(chat_id, f"❌ Errore nel download: {e}")

    show_download_button(chat_id)

def show_download_button(chat_id):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button = KeyboardButton("🔄 Scarica un altro video")
    keyboard.add(button)
    bot.send_message(chat_id, "Vuoi scaricare un altro video?", reply_markup=keyboard)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🎵 Inviami il link di YouTube per scaricare il file MP3 o MP4!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == "🔄 Scarica un altro video":
        bot.send_message(message.chat.id, "📥 Inviami il link di un altro video!")
    elif "youtube.com" in message.text or "youtu.be" in message.text:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        mp3_button = KeyboardButton("🎵 MP3")
        mp4_button = KeyboardButton("🎬 MP4")
        keyboard.add(mp3_button, mp4_button)
        bot.send_message(message.chat.id, "Scegli il formato di download:", reply_markup=keyboard)
        bot.register_next_step_handler(message, process_format_choice, message.text)
    else:
        bot.send_message(message.chat.id, "⚠️ Per favore, inviami un link di YouTube valido!")

def process_format_choice(message, url):
    if message.text == "🎵 MP3":
        download_video(url, message.chat.id, "mp3")
    elif message.text == "🎬 MP4":
        download_video(url, message.chat.id, "mp4")
    else:
        bot.send_message(message.chat.id, "⚠️ Per favore, scegli tra MP3 o MP4.")

bot.polling(timeout=200, long_polling_timeout=200)
