import os
import io
import json
import requests
import threading
import warnings
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai import Credentials, APIClient
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.signature import SignatureVerifier
from docx import Document
import pdfplumber



# Suppress pdfplumber warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pdfplumber")

# Load environment variables
load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
WATSONX_URL = os.getenv("WATSONX_URL")
WATSONX_APIKEY = os.getenv("WATSONX_APIKEY")
PROJECT_ID = os.getenv("PROJECT_ID")

# IBM Watsonx setup
credentials = Credentials(url=WATSONX_URL, api_key=WATSONX_APIKEY)
client_watsonx = APIClient(credentials)


model_general = ModelInference(
    model_id="ibm/granite-3-8b-instruct",
    api_client=client_watsonx,
    params={"decoding_method": "greedy", "max_new_tokens": 400},
    project_id=PROJECT_ID,
    verify=False
)
model_code = ModelInference(
    model_id="ibm/granite-8b-code-instruct",
    api_client=client_watsonx,
    params={"decoding_method": "greedy", "max_new_tokens": 400},
    project_id=PROJECT_ID,
    verify=False
)

app = Flask(__name__)
client = WebClient(token=SLACK_BOT_TOKEN)
signature_verifier = SignatureVerifier(SLACK_SIGNING_SECRET)

# In-memory store to avoid duplicate event processing
processed_event_ids = set()


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
            "Rewrite the message below in a professional, corporate tone, making it sound more formal and polished. Use formal business language and ensure the message remains clear and appropriate for a professional setting. Respond with only the rewritten message, dont write in a mail format this is for chat, no extra commentary.\n\n"
            f"Original message:\n{text}"
        )
    return text

def async_generate_and_post(response_url, text, user_id, mode):
    try:
        prompt = build_prompt(text, mode)
        response = model_general.generate_text(prompt)
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


def send_dm(user_id, text):
    if not text:
        return
    try:
        client.chat_postMessage(channel=user_id, text=text)
    except SlackApiError as e:
        print(f"Error sending DM: {e.response['error']}")

def download_file(file_url):
    try:
        headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
        resp = requests.get(file_url, headers=headers)
        if resp.status_code == 200:
            return resp.content
    except Exception as e:
        print(f"Download error: {e}")
    return None


def extract_pdf_text(file_content):
    try:
        text = ""
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error extracting text from PDF: {e}"


def extract_docx_text(file_content):
    try:
        doc = Document(io.BytesIO(file_content))
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
        return f"Error extracting text from DOCX: {e}"


def add_sassy_comments(text, model):
    prompt = (
        "Add sassy, humorous comments to the following text. Keep the original text unchanged, "
        "just insert comments where appropriate using inline reviewer notes. Make it fun but insightful:\n\n" + text
    )
    try:
        resp = model.generate_text(prompt)
        return resp if isinstance(resp, str) else resp.get("generated_text", "")
    except Exception as e:
        return f"Error generating comments: {e}"


def handle_event(event):
    """
    Process a single Slack event asynchronously.
    """
    event_type = event.get("type")
    # Chat message in DM
    if event_type == "message" and event.get("channel_type") == "im" and "subtype" not in event:
        user_id = event.get("user")
        bot_id = client.auth_test()["user_id"]
        if user_id == bot_id:
            return
        user_msg = event.get("text", "").strip()
        if not user_msg:
            return
        prompt = (
            "You're a sassy, humorous, but helpful virtual assistant. Reply playfully to this user message, but still provide useful info if needed. Avoid being robotic. No extra commentary.Think snarky but charming:\n\n" +
            f"{user_msg}"
        )
        try:
            resp = model_general.generate_text(prompt)
            reply = resp if isinstance(resp, str) else str(resp)
        except Exception as e:
            reply = f"Oops! I tried to sass you but got stage fright: {e}"
        send_dm(user_id, reply)

    # File shared event
    elif event_type == "file_shared":
        file_id = event.get("file_id")
        try:
            info = client.files_info(file=file_id)["file"]
            url = info["url_private_download"]
            ftype = info["filetype"]
            fname = info["name"]
            uid = info.get("user")
        except Exception as e:
            print(f"files_info error: {e}")
            return
        content = download_file(url)
        if not content:
            send_dm(uid, "Couldn't download the file, please retry.")
            return
        if ftype in ("pdf", "docx"):
            text = extract_pdf_text(content) if ftype == "pdf" else extract_docx_text(content)
            model_used = model_general
        else:
            try:
                text = content.decode("utf-8")
            except:
                text = "[Unable to decode file content]"
            model_used = model_code
        comment = add_sassy_comments(text, model_used)
        send_dm(uid, f"Here's your annotated `{fname}`:\n\n{comment}")

@app.route("/slack/events", methods=["POST"])
def slack_events():
    # Verify request signature
    if not signature_verifier.is_valid_request(request.get_data(), request.headers):
        return "Invalid signature", 403

    data = request.json
    # URL verification challenge
    if "challenge" in data:
        return jsonify({"challenge": data["challenge"]})

    event_id = data.get("event_id")
    if not event_id or event_id in processed_event_ids:
        return jsonify({"status": "ignored"})
    processed_event_ids.add(event_id)

    event = data.get("event", {})
    # Dispatch event to background thread
    threading.Thread(target=handle_event, args=(event,)).start()

    return jsonify({"status": "received"})


@app.route("/healthz")
def health_check():
    return "LucidLayer backend is alive!", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
