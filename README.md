# Discord Status Bot

[![MIT License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/buhhhrandon/discord-status-bot)](https://github.com/buhhhrandon/discord-status-bot)
[![Python Version](https://img.shields.io/badge/python-3.12-%23000000)](https://www.python.org/)
![Issues](https://img.shields.io/github/issues/buhhhrandon/discord-status-bot)
![Stars](https://img.shields.io/github/stars/buhhhrandon/discord-status-bot)
![Forks](https://img.shields.io/github/forks/buhhhrandon/discord-status-bot)
[![Deploy on Railway](https://img.shields.io/badge/Deploy-Railway-black?logo=railway&style=flat)](https://railway.app)

---

## 🤖 Add to Your Server

[![Add Bot to Server](https://img.shields.io/badge/Invite%20Bot-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.com/oauth2/authorize?client_id=1390854957195985029&permissions=1117200&integration_type=0&scope=applications.commands+bot)

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
   ```env
   DISCORD_TOKEN=your-bot-token-here
   GUILD_ID=your-discord-server-id
   ONLINE_CHANNEL_ID=channel-id-for-online
   VC_CHANNEL_ID=channel-id-for-voice
   MUSIC_CHANNEL_ID=channel-id-for-music

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