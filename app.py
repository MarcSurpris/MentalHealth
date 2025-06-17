from flask import Flask, render_template, request, jsonify
import requests
from dotenv import load_dotenv
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
XAI_API_KEY = os.getenv("XAI_API_KEY")
if not XAI_API_KEY:
    logger.error("XAI_API_KEY environment variable not set")
    raise ValueError("XAI_API_KEY environment variable not set")

app = Flask(__name__)

def gpt_response(user_input):
    """Fetch response from xAI API with error handling."""
    if not user_input or not isinstance(user_input, str):
        logger.warning("Invalid user input received")
        return "Please provide a valid message."

    messages = [
        {
            "role": "system",
            "content": (
                "You are a compassionate mental health assistant. "
                "Respond in a calm, supportive, and empathetic tone. "
                "Avoid giving medical advice. Always suggest professional help if needed."
            )
        },
        {"role": "user", "content": user_input}
    ]
    headers = {
        "Authorization": f"Bearer {XAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "grok-3",  # Verify model name at https://x.ai/api
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 150
    }
    try:
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=10  # Add timeout for reliability
        )
        response.raise_for_status()
        response_data = response.json()
        logger.info("Successfully fetched response from xAI API")
        return response_data["choices"][0]["message"]["content"].strip()
    except requests.exceptions.RequestException as e:
        logger.error(f"xAI API Error: {e}")
        if e.response is not None:
            logger.error(f"Response body: {e.response.text}")
        return "I'm having trouble responding right now. Please try again later or reach out to a professional for support."

@app.route("/")
def index():
    """Render the main page."""
    try:
        return render_template("index.html")
    except Exception as e:
        logger.error(f"Error rendering index.html: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/chat", methods=["POST"])
def chat():
    """Handle chat API requests."""
    try:
        data = request.get_json()
        if not data or "message" not in data:
            logger.warning("Invalid or missing message in request")
            return jsonify({"error": "Message is required"}), 400

        user_message = data["message"]
        bot_reply = gpt_response(user_message)
        return jsonify({"response": bot_reply})
    except Exception as e:
        logger.error(f"Error in /chat endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    # For local development only; Render uses gunicorn
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)