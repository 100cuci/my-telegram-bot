import telebot
import json
import os
from datetime import datetime
import schedule
import time
import pytz
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import threading
from flask import Flask

TOKEN = os.environ.get('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)
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

@app.route('/')
def home():
    return "Bot is running!"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "😎 SELAMAT DATANG Bossku !!\n"
        "🙌🏻 BERMINAT CLAIM FREE KREDIT  RM 5 - RM 35 ?\n"
        "⚠️ Mesti Kena Join Channel\n"
        "🔜 STEP 1  \n"
        "🔜 Sile Join Channel \n"
        "🔜 STEP 2 \n"
        "🔜 Lepas Join Channel Cari Post Yang Cara Claim Free Kredit \n"
        "🎲 Semua Game Boleh Main Dan Cuci !!\n"
    )
    markup = InlineKeyboardMarkup()
    join_btn = InlineKeyboardButton("👉 Join Channel", url=CHANNEL_URL)
    markup.add(join_btn)
    bot.reply_to(message, welcome_text, reply_markup=markup)
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

def run_bot():
    print("Bot polling started")
    bot.remove_webhook()
    bot.polling()

def run_schedule():
    schedule_report()

def run_web():
    port = int(os.environ.get("PORT", 81))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    threading.Thread(target=run_schedule, daemon=True).start()
    run_web()
