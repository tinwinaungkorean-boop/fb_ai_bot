import os, requests
from flask import Flask, request

app = Flask(__name__)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
FB_PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "myai123")

@app.route("/webhook", methods=['GET'])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "failed", 403

@app.route("/webhook", methods=['POST'])
def handle_messages():
    data = request.json
    try:
        if data.get('object') == 'page':
            for entry in data['entry']:
                for event in entry.get('messaging', []):
                    if event.get('message') and event['message'].get('text'):
                        reply = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                            json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": event['message']['text']}]}
                        ).json()['choices'][0]['message']['content']
                        requests.post(f"https://graph.facebook.com/v21.0/me/messages?access_token={FB_PAGE_TOKEN}",
                            json={"recipient": {"id": event['sender']['id']}, "message": {"text": reply}})
    except: pass
    return "ok", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8000)))
