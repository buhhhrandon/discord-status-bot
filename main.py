import discord
from discord.ext import tasks
from discord import app_commands
import os
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

class StatusBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.last_channel_names = {}

    async def setup_hook(self):
        guild = discord.Object(id=GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        update_voice_channels.start(self)

bot = StatusBot()

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

@tasks.loop(seconds=60)
async def update_voice_channels(bot):
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        print("Guild not found.")
        return

    online, in_voice, listening = get_stats(guild)

    updates = [
        (ONLINE_CHANNEL_ID, f"🟢 {online} Online"),
        (VC_CHANNEL_ID, f"🔊 {in_voice} In Voice"),
        (MUSIC_CHANNEL_ID, f"🎧 {listening} Listening to Music")
    ]

    for channel_id, new_name in updates:
        channel = guild.get_channel(channel_id)
        if not channel:
            print(f"Channel ID {channel_id} not found.")
            continue

        if bot.last_channel_names.get(channel_id) == new_name:
            print(f"No change in {channel.name} — skipping.")
            continue

        try:
            await channel.edit(name=new_name)
            bot.last_channel_names[channel_id] = new_name
            print(f"✅ Updated: {new_name}")
        except discord.HTTPException as e:
            print(f"⚠️ Error updating {channel.name}: {e}")

@bot.tree.command(name="status", description="Show server activity stats")
async def status_command(interaction: discord.Interaction):
    await interaction.response.defer()
    guild = interaction.guild
    if not guild:
        await interaction.followup.send("This command must be used in a server.")
        return

    online, in_voice, listening = get_stats(guild)
    msg = (
        f"🟢 **Online Members:** {online}\n"
        f"🔊 **In Voice Channels:** {in_voice}\n"
        f"🎧 **Listening to Music:** {listening}"
    )
    await interaction.followup.send(msg)

bot.run(TOKEN)
