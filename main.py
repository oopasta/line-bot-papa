from flask import Flask, request, abort, send_from_directory
import os
import random
import datetime
import pytz
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, ImageSendMessage, TextSendMessage

app = Flask(__name__, static_url_path='/static')

# 設定 LINE Channel 資訊（你自己的）
CHANNEL_ACCESS_TOKEN = 'YOUR_CHANNEL_ACCESS_TOKEN'
CHANNEL_SECRET = 'YOUR_CHANNEL_SECRET'

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# 設定你們的 LINE 群組 ID（實際測試）
TARGET_GROUP_ID = 'YOUR_GROUP_ID'

@app.route("/", methods=['GET'])
def home():
    return "LINE Bot is running."

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 提供喚醒用的 ping 路徑
@app.route("/ping", methods=['GET'])
def ping():
    return "I'm awake!"

# 接收文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print(f"收到訊息：{event.message.text} 來自：{event.source}")

# 每天早上 08:00 傳送不重複隨機圖片
@app.route("/push", methods=['GET'])
def push_image():
    static_folder = './static'
    used_log_path = 'used_images.txt'

    # 所有圖片檔案
    image_files = [f for f in os.listdir(static_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not image_files:
        return 'No images available.'

    # 已使用過的圖片紀錄
    used_images = []
    if os.path.exists(used_log_path):
        with open(used_log_path, 'r') as f:
            used_images = f.read().splitlines()

    # 篩選出未使用的圖片
    available_images = [f for f in image_files if f not in used_images]

    # 如果全部都用過，就重置 used_images
    if not available_images:
        used_images = []
        available_images = image_files

    # 隨機選擇圖片
    selected_image = random.choice(available_images)

    # 儲存這次使用紀錄
    used_images.append(selected_image)
    with open(used_log_path, 'w') as f:
        f.write('\n'.join(used_images))

    image_url = f'https://your-render-url.onrender.com/static/{selected_image}'

    # 先送出一段文字問候語
    text_message = TextSendMessage(text="估摸擰兩位，來看看今天的題目吧！")
    line_bot_api.push_message(TARGET_GROUP_ID, text_message)

    # 再送出圖片
    image_message = ImageSendMessage(
        original_content_url=image_url,
        preview_image_url=image_url
    )
    line_bot_api.push_message(TARGET_GROUP_ID, image_message)

    return f'Image {selected_image} (no repeat) and text pushed!'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
