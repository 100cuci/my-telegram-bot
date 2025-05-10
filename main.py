import telebot
from flask import Flask
import threading
import json
import os
from datetime import datetime
import schedule
import time
import pytz
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = '7979432043:AAE4vBiWfqB1PAjC9bOd_0t_M29rnU5mQ8k'
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
        "➡️ STEP 1\n"
        " Sile Join Channel\n"
        "➡️ STEP 2\n"
        " Lepas Join Channel Sile Lihat Dalam post ade cara Claim Free kredit\n"
        "➡️ STEP 3\n"
        "🎲 Semua Game Boleh Main Dan Cuci !!\n"
    )
    # 创建内联按钮
    markup = InlineKeyboardMarkup()
    join_btn = InlineKeyboardButton("👉 点击这里加入频道", url=CHANNEL_URL)
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
    count = sum(1 for u in users if u['date'] == today)
    total = len(users)
    msg = f"📊 今日新用户数：{count}\n👥 总用户数：{total}"
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
    bot.remove_webhook()
    bot.polling()

def run_web():
    app.run(host="0.0.0.0", port=81)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    threading.Thread(target=run_web).start()
    threading.Thread(target=schedule_report).start() 