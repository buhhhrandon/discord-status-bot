import discord
import asyncio
import json
import os
from discord.ext import commands, tasks
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
ONLINE_CHANNEL_ID = int(os.getenv("ONLINE_CHANNEL_ID"))
VC_CHANNEL_ID = int(os.getenv("VC_CHANNEL_ID"))
MUSIC_CHANNEL_ID = int(os.getenv("MUSIC_CHANNEL_ID"))

intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

def get_config():
    with open("config.json") as f:
        return json.load(f)

@bot.event
async def on_ready():
    print(f"{bot.user} is online!")
    await bot.change_presence(activity=discord.Game(name="tracking activity 🚀"))
    update_status.start()

last_counts = {
    "online": None,
    "in_voice": None,
    "listening": None
}

@tasks.loop(seconds=60)
async def update_status():
    guild = bot.get_guild(GUILD_ID)
    if guild is None:
        print("❌ Guild not found.")
        return

    online = 0
    in_voice = 0
    listening = 0

    for member in guild.members:
        if member.bot:
            continue
        if member.status != discord.Status.offline:
            online += 1
        if member.voice and member.voice.channel:
            in_voice += 1
        if member.activities:
            for activity in member.activities:
                if isinstance(activity, discord.Spotify):
                    listening += 1
                    break

    if (online == last_counts["online"] and
        in_voice == last_counts["in_voice"] and
        listening == last_counts["listening"]):
        print("No change in status — skipping update.")
        return

    try:
        await bot.get_channel(ONLINE_CHANNEL_ID).edit(name=f"🟢 {online} Online")
        await bot.get_channel(VC_CHANNEL_ID).edit(name=f"🎙️ {in_voice} In Voice")
        await bot.get_channel(MUSIC_CHANNEL_ID).edit(name=f"🎧 {listening} Listening to Music")

        print(f"✅ Updated: 🟢 {online} | 🎙️ {in_voice} | 🎧 {listening}")
        last_counts["online"] = online
        last_counts["in_voice"] = in_voice
        last_counts["listening"] = listening

    except discord.errors.HTTPException as e:
        if e.status == 429:
            retry = e.response.headers.get("Retry-After")
            print(f"⚠️ Rate limit hit. Retry After: {retry}s")
        else:
            print(f"❌ HTTP Error: {e}")

bot.run(TOKEN)
