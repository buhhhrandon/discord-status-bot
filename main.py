import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
import json
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

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
    print(f"✅ Bot is ready. Logged in as {bot.user}")

    # Set status
    await bot.change_presence(
        activity=discord.Game(name="tracking activity 🚀"),
        status=discord.Status.online,
    )

    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash command(s).")
    except Exception as e:
        print(f"❌ Failed to sync slash commands: {e}")

    update_channels.start()

@bot.tree.command(name="status", description="View current online, voice, and music activity")
async def status_command(interaction: discord.Interaction):
    guild = bot.get_guild(GUILD_ID)
    online = sum(1 for m in guild.members if not m.bot and m.status != discord.Status.offline)
    in_voice = sum(1 for vc in guild.voice_channels for m in vc.members if not m.bot)
    listening = sum(
        1 for m in guild.members
        if not m.bot and m.activities and any(a.type == discord.ActivityType.listening for a in m.activities)
    )

    msg = f"👥 Online: {online}\n🔊 In Voice: {in_voice}\n🎧 Listening to Music: {listening}"
    await interaction.response.send_message(msg, ephemeral=True)

@tasks.loop(minutes=1)
async def update_channels():
    print("🔁 update_channels loop running...")

    guild = bot.get_guild(GUILD_ID)
    config = get_config()

    online = sum(1 for m in guild.members if not m.bot and m.status != discord.Status.offline)
    in_voice = sum(1 for vc in guild.voice_channels for m in vc.members if not m.bot)
    listening = sum(
        1 for m in guild.members
        if not m.bot and m.activities and any(a.type == discord.ActivityType.listening for a in m.activities)
    )

    for category in guild.categories:
        for channel in category.channels:
            if str(channel.id) == str(config["channels"]["online"]):
                await channel.edit(name=f"🟢 Online: {online}")
                print(f"✅ Updated Online Channel: {online}")
            elif str(channel.id) == str(config["channels"]["voice"]):
                await channel.edit(name=f"🔊 In Voice: {in_voice}")
                print(f"✅ Updated Voice Channel: {in_voice}")
            elif str(channel.id) == str(config["channels"]["music"]):
                await channel.edit(name=f"🎧 Listening: {listening}")
                print(f"✅ Updated Music Channel: {listening}")

bot.run(TOKEN)
