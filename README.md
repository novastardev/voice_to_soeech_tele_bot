# 🔊 Voice to Speech — Telegram Bot

**Built with 💛 by Novastar** 👨‍💻🇳🇬

A powerful Telegram bot that converts text to natural-sounding speech using AI-powered TTS APIs. Deploy it yourself for FREE on Render!

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Telegram](https://img.shields.io/badge/Telegram-Bot-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## ✨ Features

- 🎙️ **Text to Speech** — Convert any text into natural audio with multiple AI voices
- 🗣️ **Multiple Voices** — Choose from different voice options
- 📚 **Voice Library** — Save and replay your generated speeches
- ⚙️ **Settings** — Customize voice and manage preferences
- 🔒 **Access Control** — Admin-approved chat whitelist
- 🌐 **Web Interface** — Use the bot from any browser, no Telegram required
- 📱 **Mobile Friendly** — Responsive design for any device

---

## 🚀 Deploy on Render (FREE)

Render gives you **FREE hosting** with a custom domain! Follow these steps:

### Step 1: Fork This Repository

Click the **Fork** button on GitHub to create your own copy.

---

### Step 2: Create a Render Account

1. Go to **[render.com](https://render.com)**
2. Sign up with your **GitHub account**

---

### Step 3: Create a New Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your forked repository
3. Click **"Connect"**

---

### Step 4: Configure Your Service

Fill in these settings:

| Setting | Value |
|---|---|
| **Name** | `voice-to-speech` |
| **Region** | Choose closest to you |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python3 bot.py` |
| **Instance Type** | **Free** |

---

### Step 5: Add Environment Variables

Click **"Environment"** and add these variables:

- **`TELEGRAM_BOT_TOKEN`** — Get from [@BotFather](https://t.me/BotFather) on Telegram
- **`TTS_API_KEY`** — Your TTS.ai API key
- **`ALLOWED_CHAT_IDS`** — JSON array of allowed Telegram user IDs (e.g. `[8499843492]`)
- **`BOT_OWNER_HANDLE`** — Your Telegram username (e.g. `@novastar_dev`)

---

### Step 6: Deploy!

Click **"Create Web Service"** and wait ~2 minutes.

Your bot will be live at:
```
https://voice-to-speech.onrender.com
```

🎉 **YOUR TTS BOT IS NOW LIVE!!!**

---

## 🖥️ Run Locally

Want to run it on your own computer?

### 1. Clone the repository
```bash
git clone https://github.com/novastardev/voice_to_speech.git
cd voice_to_speech
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment variables
```bash
cp .env.example .env
```

Edit `.env` with your values.

### 4. Run the bot
```bash
python3 bot.py
```

---

## 📁 Project Structure

- `bot.py` — Telegram bot main file
- `server.py` — Web interface server
- `config.py` — Configuration loader
- `database.py` — SQLite database operations
- `tts.py` — TTS API integration
- `requirements.txt` — Python dependencies
- `.env.example` — Environment variables template

---

## 🌐 Web Interface

The web interface provides a **no-signup-needed** way to use the TTS bot:
- Type text → Select voice → Hear speech
- Works in any browser — no Telegram needed
- Fully responsive on mobile and desktop

---

## 🛠️ Built With

- **Python 3.10+**
- **python-telegram-bot** — Telegram Bot API
- **tts.ai** — AI Text-to-Speech API
- **SQLite** — User data storage
- **Flask** — Web interface framework

---

## 📝 License

**MIT License** — feel free to use, modify, and distribute!

---

## 🤝 Contributions

Contributions, issues, and feature requests are welcome!  
Open a PR or create an issue on GitHub.

---

**Built with 💛 by Novastar**

- [GitHub](https://github.com/novastardev)
- [Portfolio](https://novastar-dev.vercel.app)
- [Telegram](https://t.me/novastar)

---

**Made in Nigeria 🇳🇬**
