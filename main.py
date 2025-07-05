import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
import os
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
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)


async def update_channels():
    await bot.wait_until_ready()
    guild = bot.get_guild(GUILD_ID)

    if guild is None:
        print("❌ Guild not found.")
        return

    while not bot.is_closed():
        online_count = 0
        voice_count = 0
        listening_count = 0

        for member in guild.members:
            if member.bot:
                continue
            if member.status != discord.Status.offline:
                online_count += 1
            if member.voice and member.voice.channel:
                voice_count += 1
            if member.activities:
                for activity in member.activities:
                    if isinstance(activity, discord.Spotify):
                        listening_count += 1
                        break

        try:
            online_channel = guild.get_channel(ONLINE_CHANNEL_ID)
            vc_channel = guild.get_channel(VC_CHANNEL_ID)
            music_channel = guild.get_channel(MUSIC_CHANNEL_ID)

            if online_channel:
                await online_channel.edit(name=f"🟢 Online: {online_count}")
            if vc_channel:
                await vc_channel.edit(name=f"🔊 In Voice: {voice_count}")
            if music_channel:
                await music_channel.edit(name=f"🎧 Listening: {listening_count}")

            print(f"[{datetime.now(timezone.utc).isoformat()}] Updated: Online={online_count}, Voice={voice_count}, Music={listening_count}")

        except Exception as e:
            print(f"❌ Failed to update channels: {e}")

        await asyncio.sleep(60)


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} ({bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Slash commands synced — {len(synced)} command(s)")
    except Exception as e:
        print(f"❌ Slash command sync failed: {e}")

    # ✅ Launch background task properly
    asyncio.create_task(update_channels())


@bot.tree.command(name="status", description="View current online, voice, and music activity")
async def status_command(interaction: discord.Interaction):
    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message("❌ Command must be used in a server.", ephemeral=True)
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

    await interaction.response.send_message(
        f"🟢 Online: {online} | 🔊 In Voice: {in_voice} | 🎧 Listening: {listening}"
    )

bot.run(TOKEN)
