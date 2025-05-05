# LucidLayer

![LucidLayer Logo](images/lucidlayer_logo.png)  

LucidLayer is an AI-powered Slack assistant designed to make daily communication more engaging, creative, and human. By leveraging IBM's Granite models, LucidLayer simplifies corporate jargon, adds humor, and helps teams express their ideas in a clearer, more accessible manner. Whether you're dealing with boring reports, long emails, or dry presentations, LucidLayer turns the mundane into something more delightful.

## **Hackathon Theme: "Make Work Less Boring"**

**LucidLayer's mission aligns perfectly with the hackathon theme —** we aim to *inject creativity into the day-to-day business operations*, reducing the friction and formality of internal communication, and fostering a more innovative, open, and collaborative work environment.

---

### **How LucidLayer Addresses the Theme**

By simplifying, humanizing, and adding fun to communication, LucidLayer enhances team creativity and innovation by:

- **Transforming corporate jargon** into clear, digestible language.
- **Adding humor and simplification** to messages, reducing friction and improving engagement.
- **Offering Slack slash commands and document annotation** to make reports and discussions more playful.
- **Providing message transformation buttons** to retrofit creativity into old content.
- **Leveraging IBM Granite** to deliver context-aware, creative outputs tailored to user tone.

---

### **✨ Features**

- **Slash Command for Slack**: Instantly transform boring, formal text into something fun, simple, or corporate-friendly.
- **Message Transformation Button**: Reword Slack messages using predefined styles like humor, Gen-Z, or professional.
- **DM File Handler**: Drop a document or code file into a DM with the bot and get simplified, witty, or annotated feedback.
- **Granite Model Integration**: IBM’s latest language model powers all content rewrites.
- **Corporate Mode**: Professionalizes informal messages into polished business communication.

---

### ✅ **Work Completed**

- [x] Slack integration with slash commands and message transformation
- [x] AI-powered message transformation (simple, humor, Gen-Z, corporate)
- [x] Message transformation button for Slack messages
- [x] Document and code file handling via DM (PDF, DOCX, TXT, Python, Java, etc.)
- [x] IBM Granite model integration for all text transformations
- [x] Backend implementation using Flask (production-ready)
- [x] Successful testing in Slack workspace
- [x] Ready for deployment on Render

---

### ⏳ **Next Steps**

- [ ] Expand humor/casual tone options (e.g., sarcasm, pirate speak)
- [ ] Improve formatting and layout in annotated file outputs
- [ ] Add CI/CD pipeline with automated testing
- [ ] Improve error handling and fallback messages
- [ ] Collect more user feedback and usage analytics

---

### 🧠 **How It Works**

1. **Interact via Slack**: Use `/lucidlayer` or DM the bot with text or a file.
2. **Choose a Tone**: Specify a style like "humor", "simple", "corporate", or "genz".
3. **AI-Powered Rewriting**: Content is sent to IBM Granite and rewritten in that tone.
4. **Receive Response**: The revised message or annotated file is returned in Slack.

---

### 💥 **Impact on Creativity & Innovation**

LucidLayer is more than a bot — it's your team’s creative sidekick:

- **Boosts Innovation**: Removes communication barriers through clarity and creativity.
- **Promotes Inclusion**: Translates overly formal language into accessible content.
- **Makes Work Fun**: Adds a layer of humor to documents, chats, and brainstorming.

---

### 🧩 **How to Use on Slack**

1. **Set up**: Install LucidLayer into your Slack workspace by following the integration steps.
2. **Slash Command**: Use the `/lucidlayer` command followed by your message. Optionally, specify a transformation mode (simple, genz, humor, corporate).
3. **Document Upload**: Upload documents or code files, and LucidLayer will provide a witty, simplified, or humorous version.

### **Requirements**

- Slack workspace
- IBM API credentials (Granite model)
---

### 🚀 **Installation & Local Setup**

#### 1. **Clone the Repo**
```bash
git clone https://github.com/your-org/lucidlayer.git
cd lucidlayer
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Install Dependencies
- Create a .env file with:
```bash
SLACK_BOT_TOKEN=your-slack-bot-token
SLACK_SIGNING_SECRET=your-signing-secret
WATSONX_URL=your-watsonx-url
WATSONX_APIKEY=your-watsonx-apikey
PROJECT_ID=your-watsonx-project-id
```

#### 4. Run Locally
```bash
python main.py
```
To expose locally via ngrok:
```bash
ngrok http 5000
```
Update your Slack app’s event and command URLs to match the ngrok HTTPS URL.

#### 4. Deploy on Render
- Connect this repo to Render.
- Set build command: pip install -r requirements.txt
- Set start command: python main.py
- Add environment variables via Render dashboard.

### **Requirements**
- Slack workspace with a custom app installed
- IBM API credentials (Granite model via watsonx.ai)
- Python 3.8+
- Flask



### **License**
This project is licensed under the MIT License.

---

### **Contact**
For further information or contributions, please reach out to [arpitsinghgautam777@gmail.com](mailto:arpitsinghgautam777@gmail.com).
