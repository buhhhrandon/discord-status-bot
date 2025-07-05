import discord
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

client = discord.Client(intents=intents)

def get_config():
    with open("config.json") as f:
        return json.load(f)

async def update_channels():
    await client.wait_until_ready()
    guild = client.get_guild(GUILD_ID)
    if guild is None:
        print("Bot is not in the specified guild.")
        return

    while not client.is_closed():
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

            activity = member.activity
            if activity and isinstance(activity, discord.Spotify):
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

        await asyncio.sleep(60)

@client.event
async def on_ready():
    print(f"{client.user} is now running.")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="tracking activity 🚀"))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == "/status":
        guild = message.guild
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

            activity = member.activity
            if activity and isinstance(activity, discord.Spotify):
                listening += 1

        await message.channel.send(
            f"🟢 Online: {online}\n🔊 In Voice: {in_voice}\n🎧 Listening to Music: {listening}"
        )

client.loop.create_task(update_channels())
client.run(TOKEN)
