from flask import Flask, request, abort
import os
import random
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage

app = Flask(__name__, static_url_path='/static')

# LINE 設定（已填入你的實際資訊）
CHANNEL_ACCESS_TOKEN = '96/ASZx0468Dr2alabzP0GQqCwBFg+fH8UL1jN1pRlTj4sRbUWtyhF8YzZDidHciY2xmMmQCgoMo+0/e9ofWVYIJi4JkpsbGlBnjxC8re5tH/OCpGq77WOt0Dwm/iSfh3qKLcQFH691ewcoVFkbs8wdB04t89/1O/w1cDnyilFU='
CHANNEL_SECRET = '2e11c07ce763f34979b7e4552f6361f6'
TARGET_GROUP_ID = 'C247a269f084e5beb5d1a6c6b8cb8a453'

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/", methods=['GET'])
def home():
    return "LINE Bot is running."

@app.route("/ping", methods=['GET'])
def ping():
    return "I'm awake!"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("❌ 簽章驗證失敗！請檢查 CHANNEL_SECRET 是否正確")
        abort(400)
    except Exception as e:
        print(f"❌ handler.handle 發生錯誤：{e}")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    group_id = getattr(event.source, 'group_id', None)
    user_id = getattr(event.source, 'user_id', None)

    # 發送 groupId 給你自己
    if group_id:
        line_bot_api.push_message(
            'U460988eb053cfa4e5218716ba1234fb6',  # 你的 user ID
            TextSendMessage(text=f"👥 來自群組，groupId 是：{group_id}")
        )

    # 也可通知自己收到個人訊息（可選）
    if user_id:
        line_bot_api.push_message(
            'U460988eb053cfa4e5218716ba1234fb6',
            TextSendMessage(text="👤 收到你的個人訊息")
        )



@app.route("/push", methods=['GET'])
def push_image():
    static_folder = './static'
    used_log_path = 'used_images.txt'

    image_files = [f for f in os.listdir(static_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not image_files:
        return 'No images available.'

    used_images = []
    if os.path.exists(used_log_path):
        with open(used_log_path, 'r') as f:
            used_images = f.read().splitlines()

    available_images = [f for f in image_files if f not in used_images]
    if not available_images:
        used_images = []
        available_images = image_files

    selected_image = random.choice(available_images)
    used_images.append(selected_image)
    with open(used_log_path, 'w') as f:
        f.write('\n'.join(used_images))

    image_url = f"https://line-bot-papa.onrender.com/static/{selected_image}"

    line_bot_api.push_message(
        TARGET_GROUP_ID,
        TextSendMessage(text="估摸擰兩位，來看看今天的題目吧！")
    )
    line_bot_api.push_message(
        TARGET_GROUP_ID,
        ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)
    )

    return '', 204

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
