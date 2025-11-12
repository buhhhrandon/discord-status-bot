import discord
import asyncio
import os
import json
from datetime import datetime, timedelta, timezone, time as dtime
from zoneinfo import ZoneInfo
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()

# ====== REQUIRED ENV VARS (Railway Variables) ======
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
ONLINE_CHANNEL_ID = int(os.getenv("ONLINE_CHANNEL_ID"))
VC_CHANNEL_ID = int(os.getenv("VC_CHANNEL_ID"))
MUSIC_CHANNEL_ID = int(os.getenv("MUSIC_CHANNEL_ID"))
OWNER_ID = int(os.getenv("OWNER_ID", "96749215761338368"))  # your Discord USER ID

# Optional fallback: channel to ping if DMs are closed (e.g., a private admin channel)
ADMIN_CHANNEL_ID = int(os.getenv("ADMIN_CHANNEL_ID", "0"))

# One-time override to force a startup DM on next boot (set to "1")
FORCE_STARTUP_REMINDER = os.getenv("FORCE_STARTUP_REMINDER", "0") == "1"

# Timezone fixed to Dallas, TX
LOCAL_TZ = ZoneInfo("America/Chicago")

# ====== REMINDER SETTINGS ======
REMINDER_FILE = "/data/last_status_reminder.json"  # mount a Railway volume at /data
REMINDER_INTERVAL = timedelta(days=25)
INITIAL_COOLDOWN = timedelta(hours=20)        # avoids spam if you redeploy repeatedly in one day
RECENT_SEND_WINDOW = timedelta(minutes=5)     # dedupe guard

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

# Lock is created in on_ready() to bind to the running loop
reminder_lock: asyncio.Lock | None = None


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
    global reminder_lock
    if reminder_lock is None:
        reminder_lock = asyncio.Lock()

    async with reminder_lock:
        if not OWNER_ID:
            print("OWNER_ID not set; cannot send reminder.")
            return

        now = datetime.now(timezone.utc)
        last = load_last_reminder()

        # Dedupe: if something else just sent one moments ago, skip
        if last and (now - last) < RECENT_SEND_WINDOW:
            print("Reminder suppressed: recent send detected.")
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
            save_last_reminder(now)
            print(f"Sent {reason} reminder DM to owner.")
        except Exception as e:
            print(f"Failed to DM owner: {e}")
            if ADMIN_CHANNEL_ID:
                try:
                    ch = bot.get_channel(ADMIN_CHANNEL_ID)
                    if ch:
                        await ch.send(f"<@{OWNER_ID}> {msg}")
                        save_last_reminder(now)
                        print(f"Sent {reason} reminder in fallback channel.")
                except Exception as ee:
                    print(f"Fallback channel send failed: {ee}")


# Run exactly at 12:00 PM America/Chicago every day; only send if >= 25 days elapsed
@tasks.loop(time=dtime(12, 0, tzinfo=LOCAL_TZ))
async def reminder_noon():
    now = datetime.now(timezone.utc)
    last = load_last_reminder()
    if last is None or now - last >= REMINDER_INTERVAL:
        await send_reminder("noon/25-day")


async def initial_reminder_now():
    """
    Send one reminder immediately on startup (now), then noon schedule takes over.
    Cooldown suppresses repeats on rapid redeploys unless FORCE_STARTUP_REMINDER=1.
    """
    now = datetime.now(timezone.utc)
    last = load_last_reminder()

    if FORCE_STARTUP_REMINDER:
        await send_reminder("initial/forced")
        return

    if last is None or now - last >= INITIAL_COOLDOWN:
        await send_reminder("initial/startup")
    else:
        print("Initial reminder suppressed (cooldown active).")


# ====== Bot logic ======
@bot.event
async def on_ready():
    global reminder_lock
    reminder_lock = asyncio.Lock()  # bind lock to this loop

    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(
        status=discord.Status.dnd,
        activity=discord.Game(name="tracking activity 🚀")
    )

    update_channels.start()

    # Send NOW (respects cooldown unless forced), then start the noon-only scheduler
    await initial_reminder_now()
    reminder_noon.start()

    try:
        # Sync globally
        synced = await bot.tree.sync()
        print(f"Slash commands synced: {[cmd.name for cmd in synced]}")
        print("Reminder timezone fixed to America/Chicago; noon job scheduled.")
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


# Owner-only manual trigger to DM now
@bot.tree.command(name="remindme", description="Owner-only: DM me a /status reminder now")
async def remindme_command(interaction: discord.Interaction):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("This command is owner-only.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    await send_reminder("manual/slash")
    await interaction.followup.send("Sent you a DM reminder.", ephemeral=True)


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
