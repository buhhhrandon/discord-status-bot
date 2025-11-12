import discord
import asyncio
import os
import json
from datetime import datetime, timedelta, timezone
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()

# ====== REQUIRED ENV VARS (Railway Variables) ======
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
ONLINE_CHANNEL_ID = int(os.getenv("ONLINE_CHANNEL_ID"))
VC_CHANNEL_ID = int(os.getenv("VC_CHANNEL_ID"))
MUSIC_CHANNEL_ID = int(os.getenv("MUSIC_CHANNEL_ID"))
OWNER_ID = int(os.getenv("OWNER_ID", "96749215761338368"))  # <-- Your Discord USER ID (not the bot)

# Optional fallback: channel to ping if DMs are closed (e.g., a private admin channel)
ADMIN_CHANNEL_ID = int(os.getenv("ADMIN_CHANNEL_ID", "0"))

# ====== REMINDER SETTINGS ======
REMINDER_FILE = "/data/last_status_reminder.json"  # mount a Railway volume at /data
REMINDER_INTERVAL = timedelta(days=25)
INITIAL_COOLDOWN = timedelta(hours=20)  # avoids spam if you redeploy repeatedly in one day

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


# ====== Reminder helpers ======
def load_last_reminder():
    try:
        with open(REMINDER_FILE, "r") as f:
            data = json.load(f)
            return datetime.fromisoformat(data["last_reminder"])
    except Exception:
        return None


def save_last_reminder(dt: datetime):
    try:
        os.makedirs(os.path.dirname(REMINDER_FILE), exist_ok=True)
        with open(REMINDER_FILE, "w") as f:
            json.dump({"last_reminder": dt.isoformat()}, f)
    except Exception:
        # If no volume, it just won't persist (you might get more DMs after redeploys)
        pass


async def send_reminder(reason: str = "scheduled"):
    """DM the owner a /status reminder (and fall back to channel if DM fails)."""
    if not OWNER_ID:
        print("OWNER_ID not set; cannot send reminder.")
        return

    msg = (
        "⏰ **/status reminder**\n"
        "To keep the **Active Developer** badge, a *user* must run a slash command "
        "from this bot at least once every 30 days.\n\n"
        "Please run `/status` in your server."
    )
    try:
        user = await bot.fetch_user(OWNER_ID)
        await user.send(msg)
        save_last_reminder(datetime.now(timezone.utc))
        print(f"Sent {reason} reminder DM to owner.")
    except Exception as e:
        print(f"Failed to DM owner: {e}")
        if ADMIN_CHANNEL_ID:
            try:
                ch = bot.get_channel(ADMIN_CHANNEL_ID)
                if ch:
                    await ch.send(f"<@{OWNER_ID}> {msg}")
                    save_last_reminder(datetime.now(timezone.utc))
                    print(f"Sent {reason} reminder in fallback channel.")
            except Exception as ee:
                print(f"Fallback channel send failed: {ee}")


@tasks.loop(hours=24)
async def reminder_loop():
    """Checks daily; sends a DM if 25 days have passed since the last reminder."""
    now = datetime.now(timezone.utc)
    last = load_last_reminder()
    if last is None or now - last >= REMINDER_INTERVAL:
        await send_reminder("25-day")


async def initial_reminder_today():
    """
    Sends a one-time reminder on startup (today), then the 25-day cycle takes over.
    Uses a cooldown so redeploying repeatedly in the same day doesn't spam you.
    """
    now = datetime.now(timezone.utc)
    last = load_last_reminder()
    if last is None or now - last >= INITIAL_COOLDOWN:
        await send_reminder("initial/startup")
    else:
        print("Initial reminder suppressed (cooldown active).")


# ====== Bot logic ======
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(
        status=discord.Status.dnd,
        activity=discord.Game(name="tracking activity 🚀")
    )

    update_channels.start()
    reminder_loop.start()
    await initial_reminder_today()  # <-- send a DM today, then every 25 days thereafter

    try:
        # Sync globally
        synced = await bot.tree.sync()
        print(f"Slash commands synced: {[cmd.name for cmd in synced]}")
    except Exception as e:
        print(f"Failed to sync slash commands: {e}")


def count_activity(guild):
    online = sum(1 for m in guild.members if not m.bot and m.status != discord.Status.offline)
    in_voice = sum(1 for vc in guild.voice_channels for m in vc.members if not m.bot)
    listening = sum(
        1
        for m in guild.members
        if not m.bot and m.activities and any(isinstance(a, discord.Spotify) for a in m.activities)
    )
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
