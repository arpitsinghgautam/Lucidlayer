import os
import io
import requests
from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.signature import SignatureVerifier
from docx import Document
import pdfplumber
from dotenv import load_dotenv
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParams
from ibm_watsonx_ai import Credentials, APIClient

# Load environment variables
load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
WATSONX_URL = os.getenv("WATSONX_URL")
WATSONX_APIKEY = os.getenv("WATSONX_APIKEY")
PROJECT_ID = os.getenv("PROJECT_ID")
MODEL_ID = "ibm/granite-3-8b-instruct"

# IBM Watsonx setup
credentials = Credentials(url=WATSONX_URL, api_key=WATSONX_APIKEY)
client_watsonx = APIClient(credentials)
model = ModelInference(
    model_id=MODEL_ID,
    api_client=client_watsonx,
    params={"decoding_method": "greedy", "max_new_tokens": 400},
    project_id=PROJECT_ID,
    verify=False
)

app = Flask(__name__)
client = WebClient(token=SLACK_BOT_TOKEN)
signature_verifier = SignatureVerifier(SLACK_SIGNING_SECRET)

def send_dm(user_id, text):
    try:
        client.chat_postMessage(
            channel=user_id,
            text=text
        )
    except SlackApiError as e:
        print(f"Error sending DM: {e.response['error']}")

@app.route("/slack/events", methods=["POST"])
def slack_events():
    if not signature_verifier.is_valid_request(request.get_data(), request.headers):
        return "Request verification failed", 403

    data = request.json
    if "challenge" in data:
        return jsonify({"challenge": data["challenge"]})

    if "event" in data:
        event = data["event"]
        if "subtype" not in event and event.get("channel_type") == "im":
            user_id = event.get("user")
            channel = event.get("channel")

            if "files" in event:
                file = event["files"][0]
                file_url = file["url_private"]
                file_type = file["filetype"]
                file_name = file["name"]

                file_content = download_file(file_url)
                if file_content is None:
                    send_dm(user_id, "Couldn't download the file. Please try again.")
                    return jsonify({"status": "file download failed"})

                if file_type == "pdf":
                    text = extract_pdf_text(file_content)
                elif file_type == "docx":
                    text = extract_docx_text(file_content)
                else:
                    text = file_content.decode("utf-8")

                commented_text = add_sassy_comments(text)
                send_dm(user_id, f"Here's your fun-annotated `{file_name}` with some sass:\n\n{commented_text[:3000]}")

    return jsonify({"status": "ok"})

def download_file(file_url):
    try:
        headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
        response = requests.get(file_url, headers=headers)
        if response.status_code == 200:
            return response.content
        else:
            print(f"Failed to download file: {response.status_code}")
            return None
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
        return f"Error extracting text from PDF: {str(e)}"

def extract_docx_text(file_content):
    try:
        doc = Document(io.BytesIO(file_content))
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        return f"Error extracting text from DOCX: {str(e)}"

def add_sassy_comments(text):
    try:
        prompt = (
            "Add sassy, humorous comments to the following text. Keep the original text unchanged, just insert comments where appropriate using the style of inline reviewer notes (e.g., # Wow, someone really likes big words here!). Make it fun but still insightful.\n\n"
            f"{text}"
        )
        response = model.generate_text(prompt)
        return response.get("generated_text", "[Error: No response from WatsonX model]")
    except Exception as e:
        return f"Error during comment generation: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True, port=5000)