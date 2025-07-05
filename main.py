import discord
from discord.ext import tasks
from discord import app_commands
import os
from dotenv import load_dotenv
import json
import asyncio

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
tree = app_commands.CommandTree(client)

def get_config():
    with open("config.json") as f:
        return json.load(f)

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print("✅ Slash commands synced")
    client.loop.create_task(update_channel_names())
    await client.change_presence(activity=discord.Game(name="tracking activity 🚀"))

async def update_channel_names():
    await client.wait_until_ready()
    guild = client.get_guild(GUILD_ID)

    while not client.is_closed():
        online = 0
        in_voice = 0
        listening = 0

        for member in guild.members:
            if member.bot:
                continue
            if member.status != discord.Status.offline:
                online += 1
            if member.voice:
                in_voice += 1
            if member.activities:
                for activity in member.activities:
                    if isinstance(activity, discord.Spotify):
                        listening += 1
                        break

        try:
            online_channel = guild.get_channel(ONLINE_CHANNEL_ID)
            vc_channel = guild.get_channel(VC_CHANNEL_ID)
            music_channel = guild.get_channel(MUSIC_CHANNEL_ID)

            if online_channel:
                await online_channel.edit(name=f"🟢 Online Members: {online}")
            if vc_channel:
                await vc_channel.edit(name=f"🔊 In Voice: {in_voice}")
            if music_channel:
                await music_channel.edit(name=f"🎧 Listening to Music: {listening}")
        except Exception as e:
            print(f"❌ Failed to update channels: {e}")

        await asyncio.sleep(60)

@tree.command(name="status", description="Show current server activity", guild=discord.Object(id=GUILD_ID))
async def status(interaction: discord.Interaction):
    guild = client.get_guild(GUILD_ID)
    online = sum(1 for m in guild.members if not m.bot and m.status != discord.Status.offline)
    in_voice = sum(1 for m in guild.members if not m.bot and m.voice)
    listening = 0

    for m in guild.members:
        if m.bot:
            continue
        for activity in m.activities:
            if isinstance(activity, discord.Spotify):
                listening += 1
                break

    embed = discord.Embed(title="📊 Server Activity", color=discord.Color.blue())
    embed.add_field(name="🟢 Online Members", value=online)
    embed.add_field(name="🔊 In Voice", value=in_voice)
    embed.add_field(name="🎧 Listening to Music", value=listening)
    await interaction.response.send_message(embed=embed, ephemeral=False)

client.run(TOKEN)
