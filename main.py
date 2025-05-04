import os
import json
import requests
import threading
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from ibm_watsonx_ai import APIClient
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

# Load environment variables
load_dotenv()

WATSONX_URL = os.getenv("WATSONX_URL")
WATSONX_APIKEY = os.getenv("WATSONX_APIKEY")
PROJECT_ID = os.getenv("PROJECT_ID")
MODEL_ID = "ibm/granite-3-8b-instruct"

app = Flask(__name__)

# IBM Watsonx setup
credentials = Credentials(url=WATSONX_URL, api_key=WATSONX_APIKEY)
client = APIClient(credentials)
model = ModelInference(
    model_id=MODEL_ID,
    api_client=client,
    params={"decoding_method": "greedy", "max_new_tokens": 200},
    project_id=PROJECT_ID,
    verify=False
)

def build_prompt(text, mode="simple"):
    if mode == "simple":
        return (
            "Rewrite the message below in simpler, more accessible language while keeping the meaning intact. Respond with only the rewritten message, no extra commentary.\n\n"
            f"Original message:\n{text}"
        )
    elif mode == "genz":
        return (
            "You are a Gen Z content creator. Rewrite the message below using a casual, relatable tone that reflects Gen Z language and humor. Keep it understandable and avoid slang that might confuse readers. Respond with only the rewritten message, no extra commentary.\n\n"
            f"Original message:\n{text}"
        )
    elif mode == "humor":
        return (
            "Roast the message below in a playful, witty, and light-hearted manner, as if a person was humorously responding to the request. The roast should make fun of the situation or the request, but keep it light-hearted and harmless. Do not mention AI or anything about your abilities, just focus on humorously reacting to the message. Respond with only the rewritten message, no extra commentary.\n\n"
            f"Original message:\n{text}"
        )
    elif mode == "corporate":
        return (
            "Rewrite the message below in a professional, corporate tone, making it sound more formal and polished. Use formal business language and ensure the message remains clear and appropriate for a professional setting. Respond with only the rewritten message, no extra commentary.\n\n"
            f"Original message:\n{text}"
        )
    return text

def async_generate_and_post(response_url, text, user_id, mode):
    try:
        prompt = build_prompt(text, mode)
        response = model.generate_text(prompt)
        formatted_response = {
            # "response_type": "in_channel",
            "response_type": "ephemeral",
            "text": f"<@{user_id}>\n*{mode.upper()} version:*\n{response}"
        }
        requests.post(response_url, json=formatted_response)
    except Exception as e:
        error_response = {
            "response_type": "ephemeral",
            "text": f"Error generating response: {str(e)}"
        }
        requests.post(response_url, json=error_response)

@app.route("/slack/lucidlayer", methods=["POST"])
def handle_slash_command():
    data = request.form
    message = data.get("text", "")
    user_id = data.get("user_id")
    response_url = data.get("response_url")
    mode = "simple"  # default

    parts = message.split(" ", 1)
    if parts[0].lower() in {"simple", "genz", "humor", "corporate"}:
        mode = parts[0].lower()
        text = parts[1] if len(parts) > 1 else ""
    else:
        text = message

    threading.Thread(target=async_generate_and_post, args=(response_url, text, user_id, mode)).start()

    return jsonify({
        "response_type": "ephemeral",
        "text": f"Working on your *{mode}* rewrite... you'll see it shortly!"
    })

@app.route("/healthz")
def health_check():
    return "LucidLayer backend is alive!", 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
