import discord
import asyncio
import os
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
ONLINE_CHANNEL_ID = int(os.getenv("ONLINE_CHANNEL_ID"))
VC_CHANNEL_ID = int(os.getenv("VC_CHANNEL_ID"))
MUSIC_CHANNEL_ID = int(os.getenv("MUSIC_CHANNEL_ID"))

intents = discord.Intents.default()
intents.guilds = True
intents.presences = True
intents.members = True
intents.voice_states = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

last_names = {
    "online": "",
    "voice": "",
    "music": ""
}

@client.event
async def on_ready():
    print(f"{client.user} is online!")

    await client.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name="tracking activity 🚀"
    ))

    try:
        synced = await tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"Synced {len(synced)} command(s) to guild {GUILD_ID}")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

    guild = client.get_guild(GUILD_ID)
    client.online_channel = guild.get_channel(ONLINE_CHANNEL_ID)
    client.vc_channel = guild.get_channel(VC_CHANNEL_ID)
    client.music_channel = guild.get_channel(MUSIC_CHANNEL_ID)

    while True:
        await update_channel_names(guild)
        await asyncio.sleep(60)

async def update_channel_names(guild):
    online = 0
    voice = 0
    music = 0

    for member in guild.members:
        if member.bot:
            continue
        if member.status != discord.Status.offline:
            online += 1
        if member.voice and member.voice.channel:
            voice += 1
        if member.activity and getattr(member.activity, 'type', None) == discord.ActivityType.listening:
            music += 1

    names = {
        "online": f"🟢 {online} Online",
        "voice": f"🎙️ {voice} In Voice",
        "music": f"🎧 {music} Listening to Music"
    }

    updated = False

    if client.online_channel and names["online"] != last_names["online"]:
        await safe_edit(client.online_channel, names["online"])
        last_names["online"] = names["online"]
        updated = True

    if client.vc_channel and names["voice"] != last_names["voice"]:
        await safe_edit(client.vc_channel, names["voice"])
        last_names["voice"] = names["voice"]
        updated = True

    if client.music_channel and names["music"] != last_names["music"]:
        await safe_edit(client.music_channel, names["music"])
        last_names["music"] = names["music"]
        updated = True

    if updated:
        print(f"✅ Updated: {names['online']} | {names['voice']} | {names['music']}")
    else:
        print("No change in status — skipping update.")

async def safe_edit(channel, name):
    try:
        await channel.edit(name=name)
    except discord.HTTPException as e:
        print(f"⚠️ Could not edit {channel.name}: {e}")

@tree.command(name="status", description="Check bot status", guild=discord.Object(id=GUILD_ID))
async def status(interaction: discord.Interaction):
    await interaction.response.send_message("I'm tracking activity 🚀", ephemeral=True)

client.run(TOKEN)
