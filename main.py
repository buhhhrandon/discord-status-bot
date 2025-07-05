import discord
import asyncio
import os
from discord.ext import commands
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

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} ({bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Slash commands synced — {len(synced)} command(s)")
    except Exception as e:
        print(f"❌ Slash command sync failed: {e}")

async def update_channels():
    await bot.wait_until_ready()
    guild = bot.get_guild(GUILD_ID)

    while not bot.is_closed():
        online = sum(1 for member in guild.members if not member.bot and member.status != discord.Status.offline)
        in_voice = sum(1 for vc in guild.voice_channels for member in vc.members if not member.bot)
        listening = sum(1 for member in guild.members if not member.bot and member.activities and any(a.type == discord.ActivityType.listening for a in member.activities))

        try:
            updates = []

            online_channel = guild.get_channel(ONLINE_CHANNEL_ID)
            new_online_name = f"🟢 Online: {online}"
            if online_channel and online_channel.name != new_online_name:
                await online_channel.edit(name=new_online_name)
                updates.append(f"Online: {online}")

            vc_channel = guild.get_channel(VC_CHANNEL_ID)
            new_vc_name = f"🔊 In Voice: {in_voice}"
            if vc_channel and vc_channel.name != new_vc_name:
                await vc_channel.edit(name=new_vc_name)
                updates.append(f"In Voice: {in_voice}")

            music_channel = guild.get_channel(MUSIC_CHANNEL_ID)
            new_music_name = f"🎧 Listening: {listening}"
            if music_channel and music_channel.name != new_music_name:
                await music_channel.edit(name=new_music_name)
                updates.append(f"Listening: {listening}")

            if updates:
                print(f"✅ Channel Updates — {' | '.join(updates)}")

        except discord.HTTPException as e:
            if e.status == 429:
                print("⚠️ Rate limited by Discord. Retrying after delay.")
            else:
                print(f"❌ Failed to update channels: {e}")

        await asyncio.sleep(60)

@bot.tree.command(name="status", description="View current online, voice, and music activity")
async def status(interaction: discord.Interaction):
    guild = bot.get_guild(GUILD_ID)
    online = sum(1 for member in guild.members if not member.bot and member.status != discord.Status.offline)
    in_voice = sum(1 for vc in guild.voice_channels for member in vc.members if not member.bot)
    listening = sum(1 for member in guild.members if not member.bot and member.activities and any(a.type == discord.ActivityType.listening for a in member.activities))

    await interaction.response.send_message(
        f"🟢 **Online Members**: {online}\n"
        f"🔊 **In Voice Channels**: {in_voice}\n"
        f"🎧 **Listening to Music**: {listening}",
        ephemeral=True
    )

bot.loop.create_task(update_channels())
bot.run(TOKEN)
