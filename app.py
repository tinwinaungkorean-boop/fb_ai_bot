import os
from flask import Flask, request
from google import genai
import requests

app = Flask(__name__)

# Koyeb Environment Variables မှ ဖတ်ယူခြင်း
GEMINI_KEY = os.getenv("GEMINI_KEY")
FB_PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

client = genai.Client(api_key=GEMINI_KEY)

@app.route("/webhook", methods=['GET'])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Verification failed", 403

@app.route("/webhook", methods=['POST'])
def handle_messages():
    data = request.json
    if data.get('object') == 'page':
        for entry in data['entry']:
            for messaging_event in entry.get('messaging', []):
                if messaging_event.get('message'):
                    sender_id = messaging_event['sender']['id']
                    user_text = messaging_event['message'].get('text')
                    if user_text:
                        # Gemini AI ဖြင့် အဖြေထုတ်ခြင်း
                        response = client.models.generate_content(
                            model="gemini-2.0-flash", 
                            contents=user_text
                        )
                        send_fb_message(sender_id, response.text)
    return "ok", 200

def send_fb_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={FB_PAGE_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": message_text}}
    requests.post(url, json=payload)

if __name__ == "__main__":
    # Koyeb သည် $PORT environment variable ကို အသုံးပြုသည်
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
