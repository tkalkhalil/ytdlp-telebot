import os
import sys
import re
import logging
import shutil
from dotenv import load_dotenv

import telebot
from yt_dlp import YoutubeDL

logging.basicConfig(format="%(levelname)s:%(module)s: %(message)s")
logger = logging.getLogger(__name__)
DEBUG = "--debug" in sys.argv
logger.setLevel(logging.DEBUG if DEBUG else logging.WARNING)

load_dotenv()

token = os.environ.get('TOKEN', None)
if not token:
    logger.error("ERROR: Specify TOKEN in an environment variable!")
    exit(1)

bot = telebot.TeleBot(token)
tempdir = os.environ.get('TEMPLDIR', '/tmp/ytdlp-telebot')
os.makedirs(tempdir, exist_ok=True)

NODE_PATH = shutil.which("node") or "/usr/bin/node"
logger.info(f"Detected Node.js path: {NODE_PATH}")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Send me any YouTube or Instagram link, and I will download and send you the video file!")

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    url = message.text.strip()
    if not url.startswith("http"):
        return
    
    sent_msg = bot.reply_to(message, "⏳ Downloading your video...")
    
    ydl_opts = {
        'outtmpl': os.path.join(tempdir, '%(id)s.%(ext)s'),
        'format': 'best[filesize<50M]/best',
        'noplaylist': True,
    }
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
        if os.path.exists(filename):
            with open(filename, 'rb') as video_file:
                bot.send_video(message.chat.id, video_file, caption=info.get('title', 'Here is your video!'))
            bot.delete_message(message.chat.id, sent_msg.message_id)
            os.remove(filename)
        else:
            bot.edit_message_text("❌ Failed to find the downloaded file.", message.chat.id, sent_msg.message_id)
    except Exception as e:
        logger.error(f"Download error: {e}")
        bot.edit_message_text(f"❌ Error downloading video: {str(e)}", message.chat.id, sent_msg.message_id)

if __name__ == '__main__':
    logger.info("Bot is starting polling...")
    bot.infinity_polling()
