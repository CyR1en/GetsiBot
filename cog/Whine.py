import secrets
from discord.ext import commands, tasks

from configuration import ConfigNode


class Whine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config_file
        self.color = bot.color
        self.verified_channel = []
        self.whine_task.start()

    def cog_unload(self):
        self.whine_task.cancel()

    async def _verify_channels(self):
        for c_id in self.config.get_list_node(ConfigNode.CHANNELS):
            c = self.bot.get_channel(c_id)
            if c is not None:
                self.verified_channel.append(c)

    async def _send_random_whine(self, channel):
        msg = secrets.choice(self.config.get_list_node(ConfigNode.WHINES))
        await channel.send(msg)

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.user.mentioned_in(message):
            await self._send_random_whine(message.channel)

    @commands.group()
    @commands.is_owner()
    async def add(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Huh?")

    @add.error
    async def add_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('Only Ethan can put words in my mouth')

    @commands.command()
    async def whines(self, ctx):
        whines = self.config.get_list_node(ConfigNode.WHINES)
        await ctx.send("`{}`".format(str(whines)))

    @add.command()
    async def whine(self, ctx, *args):
        whines = self.config.get_list_node(ConfigNode.WHINES)
        for arg in args:
            whines.append(arg)
        self.config.set(ConfigNode.WHINES, str(whines))
        await ctx.send("Okay I added that whine")

    @add.command()
    async def channel(self, ctx, c_id: int):
        c_ids = self.config.get_list_node(ConfigNode.CHANNELS)
        c_ids.append(c_id)
        self.config.set(ConfigNode.CHANNELS, str(c_ids))
        await self._verify_channels()
        await ctx.send("Okay I added that channel")

    @tasks.loop(hours=6)
    async def whine_task(self):
        channel = secrets.choice(self.verified_channel)
        await self._send_random_whine(channel)

    @whine_task.before_loop
    async def before_whine(self):
        await self.bot.wait_until_ready()
        await self._verify_channels()
