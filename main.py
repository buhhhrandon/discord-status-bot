import discord
import asyncio
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
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Store last known counts to avoid unnecessary updates
last_online = None
last_in_voice = None
last_listening = None

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Game(name="tracking activity 🚀"))
    update_channels.start()
    try:
        # Sync globally (remove guild arg)
        synced = await bot.tree.sync()
        print(f"Slash commands synced: {[cmd.name for cmd in synced]}")
    except Exception as e:
        print(f"Failed to sync slash commands: {e}")

def count_activity(guild):
    online = sum(1 for m in guild.members if not m.bot and m.status != discord.Status.offline)
    in_voice = sum(1 for vc in guild.voice_channels for m in vc.members if not m.bot)
    listening = sum(1 for m in guild.members if not m.bot and m.activities and any(isinstance(a, discord.Spotify) for a in m.activities))
    return online, in_voice, listening

@tasks.loop(seconds=301)
async def update_channels():
    global last_online, last_in_voice, last_listening

    guild = bot.get_guild(GUILD_ID)
    if not guild:
        print("Guild not found.")
        return

    online, in_voice, listening = count_activity(guild)

    print(f"Activity counts - Online: {online}, In Voice: {in_voice}, Listening: {listening}")

    # Only update if counts changed
    if (online, in_voice, listening) == (last_online, last_in_voice, last_listening):
        print("No changes detected, skipping channel updates.")
        return

    try:
        await guild.get_channel(ONLINE_CHANNEL_ID).edit(name=f"🟢 Online: {online}")
        await guild.get_channel(VC_CHANNEL_ID).edit(name=f"🔊 In Voice: {in_voice}")
        await guild.get_channel(MUSIC_CHANNEL_ID).edit(name=f"🎧 Listening to Music: {listening}")
        print("Channel names updated successfully.")
        # Update last known counts
        last_online, last_in_voice, last_listening = online, in_voice, listening
    except Exception as e:
        print(f"Error updating channel names: {e}")

@bot.tree.command(name="status", description="View current online, voice, and music activity")
async def status_command(interaction: discord.Interaction):
    guild = interaction.guild
    if not guild:
        await interaction.response.send_message("This command can only be used in a server.")
        return

    online, in_voice, listening = count_activity(guild)

    embed = discord.Embed(color=discord.Color.teal())
    embed.set_author(name="StatusTracker", icon_url=bot.user.display_avatar.url)
    embed.add_field(name="🟢 Online", value=str(online), inline=False)
    embed.add_field(name="🔊 In Voice", value=str(in_voice), inline=False)
    embed.add_field(name="🎧 Listening to Music", value=str(listening), inline=False)

    await interaction.response.send_message(embed=embed)

# Test ping slash command to confirm registration
@bot.tree.command(name="ping", description="Test command to check if bot responds")
async def ping_command(interaction: discord.Interaction):
    await interaction.response.send_message("pong!")

# Debug print to show registered commands after defining them
print("Commands registered:", [cmd.name for cmd in bot.tree.walk_commands()])

bot.run(TOKEN)
