import random
from discord.ext import commands, tasks

from configuration import ConfigNode


class Whine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config_file
        self.color = bot.color
        self.verified_channel = []
        self.whine.start()

    def cog_unload(self):
        self.whine.cancel()

    async def _verify_channels(self):
        for c_id in self.config.get_list_node(ConfigNode.CHANNELS):
            c = self.bot.get_channel(c_id)
            if c is not None:
                self.verified_channel.append(c)

    @tasks.loop(hours=1)
    async def whine(self):
        channel = random.choice(self.verified_channel)
        msg = random.choice(self.config.get_list_node(ConfigNode.WHINES))
        await channel.send(msg)

    @whine.before_loop
    async def before_whine(self):
        await self.bot.wait_until_ready()
        await self._verify_channels()
