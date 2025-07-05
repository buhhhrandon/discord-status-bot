import discord
from discord.ext import tasks
import asyncio
import json
import os
from dotenv import load_dotenv

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

def get_config():
    with open("config.json") as f:
        return json.load(f)

@tasks.loop(seconds=60)
async def update_channels():
    guild = bot.get_guild(GUILD_ID)
    if guild is None:
        print("Bot is not in the specified guild.")
        return

    print("Running update_channels loop...")

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
        if isinstance(member.activity, discord.Spotify):
            listening += 1

    print(f"Updated counts — Online: {online}, In Voice: {in_voice}, Listening: {listening}")

    try:
        online_channel = guild.get_channel(ONLINE_CHANNEL_ID)
        vc_channel = guild.get_channel(VC_CHANNEL_ID)
        music_channel = guild.get_channel(MUSIC_CHANNEL_ID)

        if online_channel:
            await online_channel.edit(name=f"🟢 Online: {online}")
        if vc_channel:
            await vc_channel.edit(name=f"🔊 In Voice: {in_voice}")
        if music_channel:
            await music_channel.edit(name=f"🎧 Music: {listening}")
    except Exception as e:
        print(f"Error updating channels: {e}")

@bot.event
async def on_ready():
    print(f"{bot.user} is now running.")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="tracking activity 🚀"))
    update_channels.start()

@bot.slash_command(guild_ids=[GUILD_ID], description="Get current activity stats")
async def status(ctx):
    guild = ctx.guild
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
        if isinstance(member.activity, discord.Spotify):
            listening += 1

    await ctx.respond(
        f"🟢 Online: {online}\n🔊 In Voice: {in_voice}\n🎧 Listening to Music: {listening}",
        ephemeral=True
    )

bot.run(TOKEN)
