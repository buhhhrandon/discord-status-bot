import discord
from discord.ext import commands, tasks
import os
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

    update_voice_channel.start()


@tasks.loop(seconds=60)  # safer interval to avoid rate limits
async def update_voice_channel():
    guild = bot.get_guild(GUILD_ID)
    channel = guild.get_channel(CHANNEL_ID)
    if not channel:
        print("Voice channel not found.")
        return

    online, in_voice, listening = get_stats(guild)

    new_name = f"🟢 {online} Online | 🔊 {in_voice} VC | 🎧 {listening} Music"

    print(f"Current: {channel.name.strip()} | New: {new_name.strip()}")

    if channel.name.strip() != new_name.strip():
        try:
            await channel.edit(name=new_name)
            print(f"Updated voice channel name to: {new_name}")
        except discord.errors.HTTPException as e:
            print(f"Rate limited or failed to update channel name: {e}")
    else:
        print("No change in stats — skipping channel update.")


@bot.tree.command(name="status", description="Show server activity (online, in voice, listening to music)")
async def status(interaction: discord.Interaction):
    await interaction.response.defer()
    guild = interaction.guild

    online, in_voice, listening = get_stats(guild)

    await interaction.followup.send(
        f"**StatusTracker**\n"
        f"🟢 Online: **{online}**\n"
        f"🔊 In Voice: **{in_voice}**\n"
        f"🎧 Listening to Music: **{listening}**"
    )


@bot.event
async def setup_hook():
    bot.tree.copy_global_to(guild=discord.Object(id=GUILD_ID))
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))


bot.run(TOKEN)
