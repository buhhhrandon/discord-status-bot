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

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Game(name="tracking activity 🚀"))
    update_channels.start()
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"Slash commands synced: {[cmd.name for cmd in synced]}")
    except Exception as e:
        print(f"Failed to sync slash commands: {e}")

def count_activity(guild):
    online = sum(1 for m in guild.members if not m.bot and m.status != discord.Status.offline)
    in_voice = sum(1 for vc in guild.voice_channels for m in vc.members if not m.bot)
    listening = sum(1 for m in guild.members if not m.bot and m.activities and any(isinstance(a, discord.Spotify) for a in m.activities))
    return online, in_voice, listening

@tasks.loop(seconds=60)
async def update_channels():
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        print("Guild not found.")
        return

    online, in_voice, listening = count_activity(guild)

    try:
        await guild.get_channel(ONLINE_CHANNEL_ID).edit(name=f"🟢 Online: {online}")
        await guild.get_channel(VC_CHANNEL_ID).edit(name=f"🔊 In Voice: {in_voice}")
        await guild.get_channel(MUSIC_CHANNEL_ID).edit(name=f"🎵 Listening to Music: {listening}")
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
    embed.add_field(name="🎵 Listening to Music", value=str(listening), inline=False)

    await interaction.response.send_message(embed=embed)

bot.run(TOKEN)
