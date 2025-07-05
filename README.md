# Discord Status Bot

[![MIT License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/buhhhrandon/discord-status-bot)](https://github.com/buhhhrandon/discord-status-bot)
[![Python Version](https://img.shields.io/badge/python-3.12-%23000000)](https://www.python.org/)

---

## 📝 About

A simple Discord bot that updates designated voice channel names with real-time server stats:
- 🟢 Online members
- 🔊 In voice
- 🎧 Listening to music

Safe, lightweight, and easy to deploy anywhere.

---

## 🚀 Features

- Real-time live member status tracking  
- Smart update intervals to avoid rate limits  
- Multi-channel support  
- Supports Railway, Replit, or local deployment  
- `/status` command to manually check counts  

---

## 📦 Installation

1. **Clone the repo**
   ```bash
   git clone https://github.com/buhhhrandon/discord-status-bot.git
   cd discord-status-bot
   ```

2. **Create a `.env` file** based on `.env.example`
   ```
   DISCORD_TOKEN=your_bot_token
   GUILD_ID=your_server_id
   ```

3. **Edit `config.json`** with your channel IDs:
   ```json
   {
     "online": "channel_id_here",
     "voice": "channel_id_here",
     "music": "channel_id_here"
   }
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the bot**
   ```bash
   python main.py
   ```

---

## 🛠️ Commands

- `/status` — Manually check live counts (for admin/testing)

---

## 🛡 License

This project is licensed under the [MIT License](LICENSE).
