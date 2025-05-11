from flask import Flask, request, abort
import os
import random
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage

app = Flask(__name__, static_url_path='/static')

# LINE 設定（填入你自己的資訊）
CHANNEL_ACCESS_TOKEN = '你的 CHANNEL_ACCESS_TOKEN'
CHANNEL_SECRET = '你的 CHANNEL_SECRET'
TARGET_GROUP_ID = '你的群組 ID（例如 Cxxxxxxxxxxxxxxxxxxxx）'

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
    user_id = getattr(event.source, 'user_id', None)
    group_id = getattr(event.source, 'group_id', None)
    room_id = getattr(event.source, 'room_id', None)

    print("=" * 40)
    print(f"📩 收到訊息：{event.message.text}")
    if group_id:
        print(f"👥 來自群組：{group_id}")
    elif room_id:
        print(f"👥 來自聊天室：{room_id}")
    elif user_id:
        print(f"👤 來自用戶：{user_id}")
    else:
        print("❓ 來源無法辨識")
    print("=" * 40)

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

    image_url = f"https://你的 Render 網址/static/{selected_image}"

    # 發送開場白
    line_bot_api.push_message(
        TARGET_GROUP_ID,
        TextSendMessage(text="估摸擰兩位，來看看今天的題目吧！")
    )

    # 發送圖片
    line_bot_api.push_message(
        TARGET_GROUP_ID,
        ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)
    )

    return '', 204

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
