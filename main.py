import discord
from discord.ext import commands, tasks
import os
import json
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
CHANNELS = {
    "online": int(os.getenv("ONLINE_CHANNEL_ID")),
    "voice": int(os.getenv("VC_CHANNEL_ID")),
    "music": int(os.getenv("MUSIC_CHANNEL_ID"))
}

intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

last_stats = {"online": -1, "voice": -1, "music": -1}

@bot.event
async def on_ready():
    print(f"[{datetime.now().strftime('%I:%M:%S %p')}] Bot is online as {bot.user}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="tracking activity 🚀"))
    update_status.start()

@tasks.loop(seconds=120)  # Adjusted for safety with rate limits
async def update_status():
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        print("[Error] Guild not found.")
        return

    online = sum(1 for m in guild.members if not m.bot and m.status != discord.Status.offline)
    in_voice = sum(1 for vc in guild.voice_channels for m in vc.members if not m.bot)
    listening = sum(1 for m in guild.members if not m.bot and m.activity and getattr(m.activity, 'type', None) == discord.ActivityType.listening)

    stats = {"online": online, "voice": in_voice, "music": listening}
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
                        last_stats[key] = value
                        print(f"[Update] {key.capitalize()} updated to {value}")
                    except discord.HTTPException as e:
                        if e.status == 429:
                            retry_after = int(e.response.headers.get("Retry-After", 5))
                            print(f"[Rate Limit] Hit for {key}, retry in {retry_after}s")
                        else:
                            print(f"[Error] Failed to update {key}: {e}")

                tasks_to_run.append(edit_channel())

    for task in tasks_to_run:
        await task

@bot.slash_command(name="status", description="Check live member stats")
async def status(ctx: discord.ApplicationContext):
    guild = ctx.guild
    online = sum(1 for m in guild.members if not m.bot and m.status != discord.Status.offline)
    in_voice = sum(1 for vc in guild.voice_channels for m in vc.members if not m.bot)
    listening = sum(1 for m in guild.members if not m.bot and m.activity and getattr(m.activity, 'type', None) == discord.ActivityType.listening)

    embed = discord.Embed(title="📊 Live Server Status", color=discord.Color.green())
    embed.add_field(name="🟢 Online", value=str(online), inline=False)
    embed.add_field(name="🔊 In Voice", value=str(in_voice), inline=False)
    embed.add_field(name="🎧 Listening to Music", value=str(listening), inline=False)
    embed.set_footer(text="Updated: " + datetime.now().strftime("%I:%M %p"))

    await ctx.respond(embed=embed)

bot.run(TOKEN)
