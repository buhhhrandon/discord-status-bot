import os
import asyncio
import json
import traceback
from dotenv import load_dotenv
import discord
from discord.ext import tasks, commands

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
ONLINE_CHANNEL_ID = int(os.getenv("ONLINE_CHANNEL_ID"))
VC_CHANNEL_ID = int(os.getenv("VC_CHANNEL_ID"))
MUSIC_CHANNEL_ID = int(os.getenv("MUSIC_CHANNEL_ID"))

@bot.event
async def on_ready():
    print(f"✅ Bot is ready. Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Game(name="tracking activity 🚀"))

    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"🔁 Synced {len(synced)} slash commands.")
    except Exception as e:
        print("🔥 Error syncing slash commands:")
        traceback.print_exc()

    update_channels.start()

@tasks.loop(seconds=60)
async def update_channels():
    try:
        print("🔄 update_channels loop running...")

        guild = bot.get_guild(GUILD_ID)
        if guild is None:
            print("❌ Guild not found!")
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

        print(f"🟢 Online: {online}, 🔊 In Voice: {in_voice}, 🎧 Listening: {listening}")

        # Update channel names
        online_channel = guild.get_channel(ONLINE_CHANNEL_ID)
        vc_channel = guild.get_channel(VC_CHANNEL_ID)
        music_channel = guild.get_channel(MUSIC_CHANNEL_ID)

        if online_channel:
            await online_channel.edit(name=f"🟢 Online: {online}")
            print(f"✅ Updated Online Channel: {online}")
        else:
            print("⚠️ Online channel not found.")

        if vc_channel:
            await vc_channel.edit(name=f"🔊 In Voice: {in_voice}")
            print(f"✅ Updated Voice Channel: {in_voice}")
        else:
            print("⚠️ Voice channel not found.")

        if music_channel:
            await music_channel.edit(name=f"🎧 Listening: {listening}")
            print(f"✅ Updated Music Channel: {listening}")
        else:
            print("⚠️ Music channel not found.")

    except Exception as e:
        print("🔥 Error in update_channels loop:")
        traceback.print_exc()

# ✅ Slash command version of status
@bot.tree.command(name="status", description="View current online, voice, and music activity")
async def status_command(interaction: discord.Interaction):
    try:
        guild = interaction.guild
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

        msg = f"🟢 Online: {online}\n🔊 In Voice: {in_voice}\n🎧 Listening: {listening}"
        await interaction.response.send_message(msg)

    except Exception as e:
        print("🔥 Error in /status command:")
        traceback.print_exc()
        await interaction.response.send_message("Something went wrong while fetching the status.", ephemeral=True)

bot.run(TOKEN)
