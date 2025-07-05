
import discord
import os
from discord.ext import tasks
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

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

bot = discord.Bot(intents=intents)

previous_counts = {
    "online": None,
    "vc": None,
    "music": None
}

@bot.event
async def on_ready():
    print(f"{bot.user} is online and ready.")
    update_stats.start()

@bot.slash_command(name="status", description="Check live member stats")
async def status(ctx):
    guild = bot.get_guild(GUILD_ID)
    if guild:
        online = sum(1 for m in guild.members if not m.bot and m.status != discord.Status.offline)
        vc = sum(1 for vc in guild.voice_channels for m in vc.members if not m.bot)
        music = sum(1 for m in guild.members if getattr(m.activity, "type", None) == discord.ActivityType.listening)
        await ctx.respond(f"🟢 Online: {online}, 🔊 VC: {vc}, 🎧 Music: {music}")
    else:
        await ctx.respond("Guild not found.")

@tasks.loop(minutes=1)
async def update_stats():
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        print("Guild not found.")
        return

    online = sum(1 for m in guild.members if not m.bot and m.status != discord.Status.offline)
    vc = sum(1 for vc in guild.voice_channels for m in vc.members if not m.bot)
    music = sum(1 for m in guild.members if getattr(m.activity, "type", None) == discord.ActivityType.listening)

    print(f"[Check] Online: {online}, VC: {vc}, Music: {music}")

    if previous_counts["online"] != online:
        channel = guild.get_channel(ONLINE_CHANNEL_ID)
        if channel:
            await channel.edit(name=f"🟢 Online: {online}")
            print(f"[Update] Online updated to {online}")
        previous_counts["online"] = online

    if previous_counts["vc"] != vc:
        channel = guild.get_channel(VC_CHANNEL_ID)
        if channel:
            await channel.edit(name=f"🔊 VC: {vc}")
            print(f"[Update] Voice updated to {vc}")
        previous_counts["vc"] = vc

    if previous_counts["music"] != music:
        channel = guild.get_channel(MUSIC_CHANNEL_ID)
        if channel:
            await channel.edit(name=f"🎧 Music: {music}")
            print(f"[Update] Music updated to {music}")
        previous_counts["music"] = music

bot.run(TOKEN)
