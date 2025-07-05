import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
import time

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
ONLINE_CHANNEL_ID = int(os.getenv("ONLINE_CHANNEL_ID"))
VC_CHANNEL_ID = int(os.getenv("VC_CHANNEL_ID"))
MUSIC_CHANNEL_ID = int(os.getenv("MUSIC_CHANNEL_ID"))

# Enable all intents to ensure presence/activity tracking works
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


def get_stats(guild):
    online = 0
    in_voice = 0
    listening = 0

    for member in guild.members:
        if member.bot:
            continue
        if member.status in [discord.Status.online, discord.Status.idle, discord.Status.dnd]:
            online += 1
        if member.voice and member.voice.channel:
            in_voice += 1
        if member.activity and member.activity.type == discord.ActivityType.listening:
            listening += 1

    return online, in_voice, listening


@bot.event
async def on_ready():
    print(f"{bot.user} is online!")

    activity = discord.Activity(type=discord.ActivityType.watching, name="tracking activity 🚀")
    await bot.change_presence(status=discord.Status.online, activity=activity)

    update_voice_channels.start()


@tasks.loop(seconds=60)
async def update_voice_channels():
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        print("Guild not found.")
        return

    online, in_voice, listening = get_stats(guild)

    channel_data = [
        (ONLINE_CHANNEL_ID, f"🟢 {online} Online"),
        (VC_CHANNEL_ID, f"🎙️ {in_voice} In Voice"),
        (MUSIC_CHANNEL_ID, f"🎧 {listening} Listening to Music"),
    ]

    for channel_id, new_name in channel_data:
        channel = guild.get_channel(channel_id)
        if not channel:
            print(f"Channel ID {channel_id} not found.")
            continue

        if channel.name.strip() != new_name.strip():
            try:
                await channel.edit(name=new_name)
                print(f"Updated {channel.name} → {new_name}")
            except discord.errors.HTTPException as e:
                print(f"⚠️ Rate limit or error updating channel {channel_id}: {e}")
                if hasattr(e.response, "headers"):
                    headers = e.response.headers
                    print(f"Headers:\n"
                          f"  X-RateLimit-Limit: {headers.get('X-RateLimit-Limit')}\n"
                          f"  X-RateLimit-Remaining: {headers.get('X-RateLimit-Remaining')}\n"
                          f"  X-RateLimit-Reset: {headers.get('X-RateLimit-Reset')}\n"
                          f"  X-RateLimit-Reset-After: {headers.get('X-RateLimit-Reset-After')}\n"
                          f"  X-RateLimit-Scope: {headers.get('X-RateLimit-Scope')}\n"
                          f"  retry_after: {headers.get('retry_after')}")
                await discord.utils.sleep_until(discord.utils.utcnow() + discord.utils.timedelta(seconds=10))
        else:
            print(f"No change in {channel.name} — skipped update.")


@bot.tree.command(name="status", description="Show server activity (online, in voice, listening to music)")
async def status(interaction: discord.Interaction):
    await interaction.response.defer()
    guild = interaction.guild

    online, in_voice, listening = get_stats(guild)

    await interaction.followup.send(
        f"**StatusTracker**\n"
        f"🟢 Online: **{online}**\n"
        f"🎙️ In Voice: **{in_voice}**\n"
        f"🎧 Listening to Music: **{listening}**"
    )


@bot.event
async def setup_hook():
    bot.tree.copy_global_to(guild=discord.Object(id=GUILD_ID))
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))


bot.run(TOKEN)
