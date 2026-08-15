# 🔊 Voice to Speech — Telegram Bot

A powerful Telegram bot that converts text to natural-sounding speech using AI-powered TTS APIs. Built by **Novastar** 👨‍💻

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

## 🚀 Quick Start

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

Edit `.env` with your values:
- `TELEGRAM_BOT_TOKEN` — Get from [@BotFather](https://t.me/BotFather) on Telegram
- `TTS_API_KEY` — Your TTS.ai API key
- `ALLOWED_CHAT_IDS` — JSON array of allowed Telegram user IDs
- `BOT_OWNER_HANDLE` — Your Telegram username

### 4. Run the bot
```bash
python bot.py
```

### 5. Run the web interface
```bash
python server.py
```

---

## 📁 Project Structure

```
voice_to_speech/
├── bot.py          # Telegram bot main file
├── server.py       # Web interface server
├── config.py       # Configuration loader
├── database.py     # SQLite database operations
├── tts.py          # TTS API integration
├── requirements.txt
├── .env.example    # Environment variables template
└── README.md
```

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

MIT License — feel free to use, modify, and distribute!

---

## 🤝 Contributions

Contributions, issues, and feature requests are welcome!  
Open a PR or create an issue on GitHub.

**Built with 💛 by Novastar**  
- [GitHub](https://github.com/novastardev)
- [Portfolio](https://novastar-dev.vercel.app)
- [Telegram](https://t.me/novastar)
