import os
from flask import Flask, request
import requests

app = Flask(__name__)

# Settings from Koyeb
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
FB_PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "myai123")

@app.route("/webhook", methods=['GET'])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Verification failed", 403

@app.route("/webhook", methods=['POST'])
def handle_messages():
    data = request.json
    try:
        if data.get('object') == 'page':
            for entry in data['entry']:
                for messaging_event in entry.get('messaging', []):
                    if messaging_event.get('message'):
                        sender_id = messaging_event['sender']['id']
                        user_text = messaging_event['message'].get('text')
                        if user_text:
                            ai_reply = get_groq_response(user_text)
                            send_fb_message(sender_id, ai_reply)
    except Exception as e:
        print(f"Error: {e}")
    return "ok", 200

def get_groq_response(text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": text}]
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()['choices'][0]['message']['content']

def send_fb_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={FB_PAGE_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": message_text}}
    requests.post(url, json=payload)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
