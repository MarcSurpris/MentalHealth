from flask import Flask, render_template, request, jsonify
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
XAI_API_KEY = os.getenv("XAI_API_KEY")
if not XAI_API_KEY:
    raise ValueError("XAI_API_KEY environment variable not set")

app = Flask(__name__)

def gpt_response(user_input):
    messages = [
        {"role": "system", "content": (
            "You are a compassionate mental health assistant. "
            "Respond in a calm, supportive, and empathetic tone. "
            "Avoid giving medical advice. Always suggest professional help if needed."
        )},
        {"role": "user", "content": user_input}
    ]
    headers = {
        "Authorization": f"Bearer {XAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "grok-3",  # Adjust based on xAI's available models (check https://x.ai/api)
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 150
    }
    try:
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()  # Raises an error for 4xx/5xx responses
        response_data = response.json()
        return response_data["choices"][0]["message"]["content"].strip()
    except requests.exceptions.RequestException as e:
        print("xAI API Error:", e)
        if e.response is not None:
            print("Response body:", e.response.text)
        return "I'm having trouble responding right now. Please try again later."

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    bot_reply = gpt_response(user_message)
    return jsonify({"response": bot_reply})

if __name__ == "__main__":
    app.run(debug=True)