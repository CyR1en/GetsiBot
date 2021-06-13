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

    @commands.group()
    @commands.is_owner()
    async def remove(self, ctx):
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
        await self._mutate_whine(ctx, *args)

    @remove.command(name='whine')
    async def whine_r(self, ctx, *args):
        await self._mutate_whine(ctx, *args)

    @add.command()
    async def channel(self, ctx, c_id: int):
        await self._mutate_channel(ctx, c_id)

    @remove.command(name='channel')
    async def channel_r(self, ctx, c_id: int):
        await self._mutate_channel(ctx, c_id)

    async def _mutate_whine(self, ctx, *args):
        whines = self.config.get_list_node(ConfigNode.WHINES)
        func = whines.append if 'add' in ctx.invoked_parents else whines.remove
        for arg in args:
            func(arg)
        self.config.set(ConfigNode.WHINES, str(whines))
        op_str = 'added' if ctx.invoked_parents[0] == 'add' else 'removed'
        await ctx.send(f'Okay I {op_str} that whine')

    async def _mutate_channel(self, ctx, c_id: int):
        c_ids = self.config.get_list_node(ConfigNode.CHANNELS)
        func = c_ids.append if 'add' in ctx.invoked_parents else c_ids.remove
        func(c_id)
        self.config.set(ConfigNode.CHANNELS, str(c_ids))
        await self._verify_channels()
        op_str = 'added' if ctx.invoked_parents[0] == 'add' else 'removed'
        await ctx.send(f'Okay I {op_str} that channel')

    @commands.command()
    @commands.is_owner()
    async def interval(self, ctx, s: float, m: float, h: float):
        self.whine_task.change_interval(seconds=s, minutes=m, hours=h)
        self.whine_task.restart()
        await ctx.send(f'Interval changed to `s = {s}, m = {m}, h = {h}`')

    @commands.command()
    async def channels(self, ctx):
        c_ids = self.config.get_list_node(ConfigNode.CHANNELS)
        channel_names = [ctx.guild.get_channel(c).name for c in c_ids]
        await ctx.send("`{}`".format(str(channel_names)))

    @tasks.loop(hours=12)
    async def whine_task(self):
        channel = secrets.choice(self.verified_channel)
        await self._send_random_whine(channel)

    @whine_task.before_loop
    async def before_whine(self):
        await self.bot.wait_until_ready()
        await self._verify_channels()
