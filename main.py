import discord
from discord import app_commands
import asyncio
import os
from datetime import datetime, timezone

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.presences = True
intents.voice_states = True

class StatusTracker(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.guild_id = int(os.getenv("GUILD_ID"))
        self.vc_channel_id = int(os.getenv("VC_CHANNEL_ID"))
        self.music_channel_id = int(os.getenv("MUSIC_CHANNEL_ID"))
        self.online_channel_id = int(os.getenv("ONLINE_CHANNEL_ID"))
        self.update_interval = 60  # in seconds
        self.last_stats = {"online": 0, "voice": 0, "listening": 0}

    async def setup_hook(self):
        guild = discord.Object(id=self.guild_id)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

    async def on_ready(self):
        print(f"{self.user} is online!")
        self.loop.create_task(self.update_channels_loop())

    async def update_channels_loop(self):
        await self.wait_until_ready()
        guild = self.get_guild(self.guild_id)

        while not self.is_closed():
            online = sum(1 for m in guild.members if not m.bot and m.status != discord.Status.offline)
            in_voice = sum(1 for vc in guild.voice_channels for m in vc.members if not m.bot)
            listening = sum(1 for m in guild.members if not m.bot and m.activities and any(a.type == discord.ActivityType.listening for a in m.activities))

            # compare to last stats
            if (online, in_voice, listening) != tuple(self.last_stats.values()):
                try:
                    if online != self.last_stats["online"]:
                        await self.update_channel_name(self.online_channel_id, f"🟢 {online} Online")
                        self.last_stats["online"] = online

                    if in_voice != self.last_stats["voice"]:
                        await self.update_channel_name(self.vc_channel_id, f"🎙️ {in_voice} In Voice")
                        self.last_stats["voice"] = in_voice

                    if listening != self.last_stats["listening"]:
                        await self.update_channel_name(self.music_channel_id, f"🎧 {listening} Listening to Music")
                        self.last_stats["listening"] = listening
                except discord.HTTPException as e:
                    print(f"[{datetime.now()}] Rate limited or error: {e}")

            await asyncio.sleep(self.update_interval)

    async def update_channel_name(self, channel_id, name):
        channel = self.get_channel(channel_id)
        if channel and channel.name != name:
            await channel.edit(name=name)

client = StatusTracker()
TOKEN = os.getenv("DISCORD_TOKEN")
client.run(TOKEN)
