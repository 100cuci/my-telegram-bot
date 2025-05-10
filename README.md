# Telegram Bot

## 简介
这是一个基于 Python 的 Telegram 机器人，支持频道检测、用户统计、定时提醒等功能。

## 使用方法

1. 安装依赖  
   ```
   pip install -r requirements.txt
   ```

2. 运行  
   ```
   python main.py
   ```

## 主要依赖
- pyTelegramBotAPI
- Flask
- schedule
- pytz

## 注意事项
- TOKEN、频道名等信息已写入 main.py
- users.json 会自动生成，无需手动创建
- 请勿上传 .env 和 users.json 到 GitHub 