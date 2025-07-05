import discord
import asyncio
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

class StatusTracker(discord.Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.online_channel = None
        self.vc_channel = None
        self.music_channel = None
        self.last_online_name = ""
        self.last_vc_name = ""
        self.last_music_name = ""

    async def on_ready(self):
        print(f"{self.user} is online!")

        guild = self.get_guild(GUILD_ID)
        self.online_channel = guild.get_channel(ONLINE_CHANNEL_ID)
        self.vc_channel = guild.get_channel(VC_CHANNEL_ID)
        self.music_channel = guild.get_channel(MUSIC_CHANNEL_ID)

        # Set bot presence
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="tracking activity 🚀"))

        while True:
            await self.update_status(guild)
            await asyncio.sleep(60)

    async def update_status(self, guild):
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
            if member.activity and getattr(member.activity, 'type', None) == discord.ActivityType.listening:
                listening += 1

        # Compose new names
        online_name = f"🟢 {online} Online"
        vc_name = f"🎙️ {in_voice} In Voice"
        music_name = f"🎧 {listening} Listening to Music"

        updated = False

        # Update if names changed
        if self.online_channel and online_name != self.last_online_name:
            await self.safe_edit(self.online_channel, online_name)
            self.last_online_name = online_name
            updated = True

        if self.vc_channel and vc_name != self.last_vc_name:
            await self.safe_edit(self.vc_channel, vc_name)
            self.last_vc_name = vc_name
            updated = True

        if self.music_channel and music_name != self.last_music_name:
            await self.safe_edit(self.music_channel, music_name)
            self.last_music_name = music_name
            updated = True

        if updated:
            print(f"✅ Updated: {online_name} | {vc_name} | {music_name}")
        else:
            print("No change in status — skipping update.")

    async def safe_edit(self, channel, new_name):
        try:
            await channel.edit(name=new_name)
        except discord.HTTPException as e:
            print(f"⚠️ Rate limited or failed to edit {channel.id}: {e}")

client = StatusTracker(intents=intents)
client.run(TOKEN)
