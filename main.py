import discord
import asyncio
import json
import os
from discord.ext import commands, tasks
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

bot = commands.Bot(command_prefix='/', intents=intents)

def get_config():
    with open("config.json") as f:
        return json.load(f)

def save_config(config):
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    await bot.change_presence(activity=discord.Game(name="tracking activity 🚀"))
    update_channels.start()

@tasks.loop(minutes=2)
async def update_channels():
    guild = bot.get_guild(GUILD_ID)
    if guild is None:
        print("Guild not found.")
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

    config = get_config()
    try:
        if ONLINE_CHANNEL_ID:
            online_channel = guild.get_channel(ONLINE_CHANNEL_ID)
            if online_channel and online_channel.name != f"🟢 Online: {online}":
                await online_channel.edit(name=f"🟢 Online: {online}")
        if VC_CHANNEL_ID:
            voice_channel = guild.get_channel(VC_CHANNEL_ID)
            if voice_channel and voice_channel.name != f"🔊 In Voice: {in_voice}":
                await voice_channel.edit(name=f"🔊 In Voice: {in_voice}")
        if MUSIC_CHANNEL_ID:
            music_channel = guild.get_channel(MUSIC_CHANNEL_ID)
            if music_channel and music_channel.name != f"🎧 Listening: {listening}":
                await music_channel.edit(name=f"🎧 Listening: {listening}")
    except discord.Forbidden:
        print("Missing permissions to edit channel names.")
    except Exception as e:
        print(f"Error updating channels: {e}")

@bot.command(name="status")
async def status(ctx):
    guild = bot.get_guild(GUILD_ID)
    if guild is None:
        await ctx.send("Guild not found.")
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

    embed = discord.Embed(
        title="Server Activity",
        description=f"🟢 Online Members: `{online}`\n🔊 In Voice Channels: `{in_voice}`\n🎧 Listening to Music: `{listening}`",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

bot.run(TOKEN)
