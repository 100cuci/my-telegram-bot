import telebot
from flask import Flask, request
import threading
import json
import os
from datetime import datetime
import schedule
import time
import pytz
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging
from waitress import serve
import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 从环境变量获取配置
BOT_TOKEN = os.getenv('BOT_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
WEBHOOK_PORT = int(os.getenv('PORT', 10000))
FACEBOOK_PIXEL_ID = os.getenv('FACEBOOK_PIXEL_ID')
FACEBOOK_ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN')

# 初始化 bot 和 Flask
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

USER_FILE = 'users.json'
ADMIN_ID = 7530630528  # 请替换为你的 Telegram 用户ID
CHANNEL_USERNAME = '@Mega888100Cuci'
CHANNEL_URL = 'https://t.me/Mega888100Cuci'
MALAYSIA_TZ = pytz.timezone('Asia/Kuala_Lumpur')

def load_users():
    if not os.path.exists(USER_FILE):
        return []
    with open(USER_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def add_user(user_id, first_name, username):
    users = load_users()
    today = datetime.now(MALAYSIA_TZ).strftime('%Y-%m-%d')
    if not any(u['id'] == user_id for u in users):
        users.append({
            'id': user_id,
            'first_name': first_name,
            'username': username,
            'date': today
        })
        save_users(users)

# Facebook Conversion API 事件上报
def track_facebook_event(event_name, user_data):
    try:
        url = f'https://graph.facebook.com/v17.0/{FACEBOOK_PIXEL_ID}/events'
        data = {
            'data': [{
                'event_name': event_name,
                'event_time': int(time.time()),
                'user_data': {
                    'external_id': str(user_data.get('user_id', '')),
                    'client_user_agent': user_data.get('user_agent', ''),
                },
                'action_source': 'system_generated'
            }],
            'access_token': FACEBOOK_ACCESS_TOKEN
        }
        response = requests.post(url, json=data)
        if response.status_code == 200:
            logger.info(f"Successfully tracked {event_name} event")
        else:
            logger.error(f"Failed to track {event_name} event: {response.text}")
    except Exception as e:
        logger.error(f"Error tracking Facebook event: {e}")

# 设置 webhook
def set_webhook():
    try:
        bot.remove_webhook()
        time.sleep(1)
        bot.set_webhook(url=WEBHOOK_URL)
        logger.info(f"Webhook set to {WEBHOOK_URL}")
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")

# 启动 webhook
set_webhook()

# 处理 webhook 请求
@app.route('/', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
        bot.process_new_updates([update])
        return 'OK'
    return 'Error'

# 处理 GET 请求以保持服务活跃
@app.route('/', methods=['GET'])
def index():
    return 'Bot is running!'

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "😎 SELAMAT DATANG Bossku !!\n"
        "🙌🏻 BERMINAT CLAIM FREE KREDIT RM 35 ?\n"
        "⚠️ Sile Join Channel Dalam ade cara ke 3 company claim free kredit total RM 35\n"
        "🔜 STEP 1  \n"
        "🔜 Sile Tekan Butang Bawah Join Channel \n"
        "🔜 STEP 2 \n"
        "🔜 Lepas Join Channel Cari Post Yang Ade 3 link Claim Free Kredit \n"
        "🔜 STEP 3\n"
        "🔜 Lepas Register ID akan dapat FREE KREDIT\n"
        "🎲 FREE KREDIT Boleh Semua Game Dan Cuci !!\n"
        "🎲 Mne Company Ong Boss Boleh Cuba Topup Dan Cuci Lebih ye\n"
    )
    markup = InlineKeyboardMarkup()
    join_btn = InlineKeyboardButton("👉 Join Channel", url=CHANNEL_URL)
    markup.add(join_btn)
    bot.reply_to(message, welcome_text, reply_markup=markup)

    # 上报 Facebook Pixel 事件
    user_info = {
        'user_id': message.from_user.id,
        'username': message.from_user.username,
        'first_name': message.from_user.first_name,
        'user_agent': message.json.get('user_agent', '') if hasattr(message, 'json') else ''
    }
    track_facebook_event('StartBot', user_info)

    add_user(message.from_user.id, message.from_user.first_name, message.from_user.username)
    bot.send_message(
        ADMIN_ID, 
        f"有新用户启动了bot:\n名字: {message.from_user.first_name}\nID: {message.from_user.id}\n用户名: @{message.from_user.username if message.from_user.username else '无'}"
    )
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, message.from_user.id)
        if member.status not in ['member', 'administrator', 'creator']:
            bot.send_message(
                message.chat.id,
                "⚠️ Anda belum join channel kami! Sila join channel untuk dapatkan free kredit.\n\n" + CHANNEL_URL
            )
            track_facebook_event('NotJoinedChannel', user_info)
        else:
            track_facebook_event('JoinedChannel', user_info)
    except Exception as e:
        print(f"检测频道成员异常: {e}")
        bot.send_message(
            message.chat.id,
            "⚠️ Anda belum join channel kami! Sila join channel untuk dapatkan free kredit.\n\n" + CHANNEL_URL
        )

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "❓ Ada soalan? Sila hubungi admin atau join channel untuk maklumat lanjut.\n"
        f"👉 {CHANNEL_URL}"
    )
    bot.reply_to(message, help_text)

def send_daily_report():
    users = load_users()
    today = datetime.now(MALAYSIA_TZ).strftime('%Y-%m-%d')
    new_users = [u for u in users if u['date'] == today]
    count = len(new_users)
    total = len(users)
    usernames = '\n'.join([
        f"{u['first_name']} (@{u['username'] if u['username'] else '无'})" for u in new_users
    ])
    msg = f"📊 今日新用户数：{count}\n👥 总用户数：{total}"
    if count > 0:
        msg += f"\n\n今日新用户列表：\n{usernames}"
    else:
        msg += "\n\n今日暂无新用户。"
    bot.send_message(ADMIN_ID, msg)

def remind_users_not_in_channel():
    users = load_users()
    for user in users:
        user_id = user['id']
        try:
            member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                bot.send_message(
                    user_id,
                    "😎Bosssku Belum join Channel lgi ? tak minat claim free kredit ke ?"
                )
        except Exception as e:
            print(f"发送私信失败: {e}")
            bot.send_message(
                user_id,
                "😎Bosssku Belum join Channel lgi ? tak minat claim free kredit ke ?"
            )

def schedule_report():
    schedule.every().day.at("00:00").do(send_daily_report)
    schedule.every().day.at("00:00").do(remind_users_not_in_channel)
    while True:
        schedule.run_pending()
        time.sleep(30)

def run_flask():
    serve(app, host='0.0.0.0', port=WEBHOOK_PORT)

# 启动 Flask 服务器
flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

if __name__ == "__main__":
    threading.Thread(target=schedule_report).start()
