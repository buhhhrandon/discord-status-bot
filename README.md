# Discord Status Bot

[![MIT License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/buhhhrandon/discord-status-bot)](https://github.com/buhhhrandon/discord-status-bot)
[![Python Version](https://img.shields.io/badge/python-3.12-%23000000)](https://www.python.org/)
![Issues](https://img.shields.io/github/issues/buhhhrandon/discord-status-bot)
![Stars](https://img.shields.io/github/stars/buhhhrandon/discord-status-bot)
![Forks](https://img.shields.io/github/forks/buhhhrandon/discord-status-bot)
[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/dyoiX9?referralCode=Z2DF-e&utm_medium=integration&utm_source=template&utm_campaign=generic)

---

## 🤖 Add to Your Server

[![Add Bot to Server](https://img.shields.io/badge/Invite%20Bot-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.com/oauth2/authorize?client_id=1390854957195985029&permissions=1117200&integration_type=0&scope=applications.commands+bot)

---

## 📝 About

A simple Discord bot that updates designated voice channel names with live server activity stats:
- 🟢 Online members  
- 🔊 In voice  
- 🎧 Listening to music  

It now also includes **automated DM reminders** to help keep your **Active Developer badge** active by reminding you to use `/status` every 25 days (12:00 PM Dallas time).

Lightweight, safe, and easy to deploy anywhere — whether on **Railway** or **locally**.

---

## 🚀 Features

- 🟢 Real-time member tracking (online / voice / Spotify)  
- 💬 Auto DM reminders to the bot owner every 25 days (12 PM Dallas time)  
- 💾 Persistent data storage using a Railway volume mounted at `/data`  
- ⚙️ Owner-only `/remindme` command for manual reminders  
- 🕐 Smart cooldown to avoid duplicate DMs  
- ⚡ Rate-limit-aware channel updates  
- 🛡 Secure — `.env` ignored in GitHub, secrets stored via Railway  

---

## 🛠️ Commands

| Command | Description | Access |
|----------|--------------|--------|
| `/status` | View current online, voice, and music counts | Everyone |
| `/ping` | Simple test to check if the bot responds | Everyone |
| `/remindme` | DM the owner a `/status` reminder now | Owner only |

---

## 🚀 One-Click Deploy (Railway)

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/dyoiX9?referralCode=Z2DF-e&utm_medium=integration&utm_source=template&utm_campaign=generic)

> After clicking the button:
> 1. Select your GitHub repo (or let Railway fork it).
> 2. Add the environment variables below.
> 3. Attach a Volume mounted at **`/data`** (for reminder persistence).
> 4. Deploy and watch it go live.

<details>
<summary><b>🔑 Required Environment Variables</b></summary>

| Key | Example | Notes |
|---|---|---|
| `DISCORD_TOKEN` | `***` | Your bot token from the Discord Developer Portal |
| `GUILD_ID` | `123456789012345678` | Your server ID |
| `ONLINE_CHANNEL_ID` | `123456789012345678` | Channel for “🟢 Online” |
| `VC_CHANNEL_ID` | `123456789012345678` | Channel for “🔊 In Voice” |
| `MUSIC_CHANNEL_ID` | `123456789012345678` | Channel for “🎧 Listening to Music” |
| `OWNER_ID` | `123456789012345678` | Your Discord user ID (for DMs) |
| `ADMIN_CHANNEL_ID` *(optional)* | `123456789012345678` | Fallback channel if DMs are closed |

> To copy IDs: Discord → *Settings > Advanced > Developer Mode ON* → right-click → **Copy ID**.

</details>

<details>
<summary><b>💾 Persistent Storage</b></summary>

Attach a **Volume**:
- **Name:** anything (e.g., `bot-data`)  
- **Mount Path:** `/data`  
- **Size:** 100 MB +  

This keeps your reminder history (`last_status_reminder.json`) so you don’t get duplicate or lost DMs across restarts.

</details>

---

## 🖥️ Local Setup (Optional)

If you prefer to host the bot on your own computer instead of Railway:

1. **Clone the repo**
   ```bash
   git clone https://github.com/buhhhrandon/discord-status-bot.git
   cd discord-status-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file**
   ```env
   DISCORD_TOKEN=your-bot-token-here
   GUILD_ID=your-discord-server-id
   ONLINE_CHANNEL_ID=channel-id-for-online
   VC_CHANNEL_ID=channel-id-for-voice
   MUSIC_CHANNEL_ID=channel-id-for-music
   OWNER_ID=your-discord-user-id
   ADMIN_CHANNEL_ID=optional-fallback-channel-id
   ```

4. **(Optional)** Create a folder for reminder storage:
   ```bash
   mkdir data
   ```
   The bot saves reminder data here (like `/data` on Railway).

5. **Run the bot**
   ```bash
   python main.py
   ```

> 💡 Tip: If you want to force a reminder right away for testing, add this line to your `.env` file:
> ```
> FORCE_STARTUP_REMINDER=1
> ```

---

## 🕒 Reminder Schedule (Dallas / America Chicago)

| Event | Action |
|--------|--------|
| **Bot startup** | Sends 1 DM (if no recent reminder or cooldown expired) |
| **Every day @ 12:00 PM Dallas time** | Checks if ≥ 25 days since last reminder; sends if true |
| **`/remindme` command** | Immediate DM to owner |
| **`FORCE_STARTUP_REMINDER=1`** | Forces DM on next deploy, then resumes normal behavior |

---

## 🧠 Notes

- You can reset the reminder state by **deleting or detaching your Railway volume**.  
- All timestamps use **UTC internally** but reminders align to **America/Chicago** (Dallas time).  
- `.env` is ignored in GitHub — your bot token stays secure.  
- Forks of this repo won’t affect your hosted bot; only your instance with your token can send DMs.  
- Works seamlessly on **Railway**, but can also be run **locally** for testing or personal hosting.

---

## 🛡 License

This project is licensed under the [MIT License](LICENSE).
