import discord
from discord.ext import commands, tasks
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
CHANNELS = {
    "online": int(os.getenv("ONLINE_CHANNEL_ID")),       # 🟢 Online Members
    "voice": int(os.getenv("VC_CHANNEL_ID")),            # 🔊 In Voice
    "music": int(os.getenv("MUSIC_CHANNEL_ID"))          # 🎧 Listening to Music
}

intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Cache to store last known stats
last_stats = {"online": -1, "voice": -1, "music": -1}


def get_stats(guild):
    online = voice = music = 0
    for member in guild.members:
        if member.bot:
            continue
        if member.status in [discord.Status.online, discord.Status.idle, discord.Status.dnd]:
            online += 1
        if member.voice and member.voice.channel:
            voice += 1
        if member.activity and member.activity.type == discord.ActivityType.listening:
            music += 1
    return {"online": online, "voice": voice, "music": music}


@bot.event
async def on_ready():
    print(f"{bot.user} is online and ready.")
    activity = discord.Activity(type=discord.ActivityType.watching, name="tracking activity 🚀")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    update_channel_names.start()


@tasks.loop(seconds=45)
async def update_channel_names():
    guild = bot.get_guild(GUILD_ID)
    if guild is None:
        print("Guild not found.")
        return

    stats = get_stats(guild)
    print(f"[Check] Online: {stats['online']}, VC: {stats['voice']}, Music: {stats['music']}")

    tasks_to_run = []

    for key, value in stats.items():
        if value != last_stats[key]:
            channel_id = CHANNELS[key]
            channel = guild.get_channel(channel_id)
            if channel:
                if key == "online":
                    new_name = f"🟢 {value} Online"
                elif key == "voice":
                    new_name = f"🔊 {value} In Voice"
                elif key == "music":
                    new_name = f"🎧 {value} Listening to Music"

                async def edit_channel(channel=channel, name=new_name, key=key, value=value):
                    try:
                        await channel.edit(name=name)
                        print(f"[Update] {key.capitalize()} updated to {value}")
                        last_stats[key] = value
                    except discord.HTTPException as e:
                        if e.status == 429:
                            retry_after = int(e.response.headers.get("Retry-After", 5))
                            print(f"[Rate Limit] Hit for {key}, retrying in {retry_after}s")
                            await asyncio.sleep(retry_after)
                        else:
                            print(f"[Error] Failed to update {key} channel: {e}")

                tasks_to_run.append(edit_channel())

    if tasks_to_run:
        await asyncio.gather(*tasks_to_run)
    else:
        print("[Skip] No stat changes, update skipped.")


@bot.tree.command(name="status", description="Show server activity")
async def status(interaction: discord.Interaction):
    await interaction.response.defer()
    guild = interaction.guild
    stats = get_stats(guild)
    await interaction.followup.send(
        f"**StatusTracker**\n"
        f"🟢 Online: **{stats['online']}**\n"
        f"🔊 In Voice: **{stats['voice']}**\n"
        f"🎧 Listening to Music: **{stats['music']}**"
    )


@bot.event
async def setup_hook():
    bot.tree.copy_global_to(guild=discord.Object(id=GUILD_ID))
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))


bot.run(TOKEN)
