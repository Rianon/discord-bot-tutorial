from platform import python_version
from time import time
from datetime import datetime, timedelta
from apscheduler.triggers.cron import CronTrigger
from discord import Activity, ActivityType, Embed
from discord import __version__ as discord_version
from discord.ext.commands import Cog, Context, command
from psutil import Process, cpu_times, virtual_memory

from lib.bot import Bot
from lib.db import db

class Meta(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self._message = 'watching {prefix}help | {users:,} user(s) in {guilds:,} server(s).'
        bot.scheduler.add_job(self.set, CronTrigger(second=0))
    
    @property
    def message(self):
        # sql_query = 'SELECT Prefix FROM guilds WHERE GuildID = ?'
        # _prefix: str = db.field(sql_query, self.bot.guild.id)
        # print(f'Prefix set to: {_prefix}')
        _prefix = '.'
        return self._message.format(prefix=_prefix, users=len(self.bot.users), guilds=len(self.bot.guilds))
    
    @message.setter
    def message(self, value):
        if value.split(' '[0]) not in ('playing', 'watching', 'listening-to', 'streaming'):
            raise ValueError('Invalid activity type.')
        
        self._message = value
    
    async def set(self):
        _type, _name = self.message.split(' ', maxsplit=1)
        
        await self.bot.change_presence(activity=Activity(name=_name, type=getattr(ActivityType, _type, ActivityType.playing)))

    @command(name='setactivity', aliases=['setact', 'sa'], brief='Sets the bot activity status.')
    async def set_activity_message(self, ctx: Context, *, text: str):
        """Sets the bot activity status."""
        self.message = text
        await self.set()
    
    @command(name='ping', brief='Pings the bot.')
    async def ping_bot(self, ctx: Context):
        """Pings the bot."""
        start = time()
        message = await ctx.send(f'Pong! DWSP Latency: {self.bot.latency*1000:,.0f} ms.')
        end = time()
        await message.edit(content=f'Pong! DWSP Latency: {self.bot.latency*1000:,.0f} ms. Response time: {(end-start)*1000:,.0f} ms.')
    
    @command(name='stats', brief='Shows the bot stats.')
    async def show_bot_stats(self, ctx: Context):
        """Shows the bot stats."""
        embed = Embed(title='Bot stats',
                      colour=ctx.author.colour,
                      thumbnail = self.bot.user.avatar_url,
                      timestamp=datetime.utcnow())
        
        proc = Process()
        with proc.oneshot():
            uptime = timedelta(seconds=time() - proc.create_time())
            cpu_time = timedelta(seconds=(cpu := proc.cpu_times()).system + cpu.user)
            mem_total = virtual_memory().total / (1024**2)
            mem_of_total = proc.memory_percent()
            mem_usage = mem_total * (mem_of_total / 100)
        
        embed.add_field(name='Bot version', value=self.bot.VERSION, inline=True)
        embed.add_field(name='Python version', value=python_version(), inline=True)
        embed.add_field(name='discord.py version', value=discord_version, inline=True)
        embed.add_field(name='Uptime', value=uptime, inline=True)
        embed.add_field(name='CPU time', value=cpu_time, inline=True)
        embed.add_field(name='Memory usage', value=f'{mem_usage:,.2f} / {mem_total:,.0f} MiB ({mem_of_total:,.2f}%)', inline=True)
        embed.add_field(name='Users', value=self.bot.guild.member_count, inline=True)
        
        await ctx.send(embed=embed)
    
    @command(name='shutdown', brief='Shutting down the bot.')
    async def shutdown(self, ctx: Context):
        """Shutting down the bot."""
        await ctx.send('Shutting down...')
        
        db.commit()
        db.close()
        
        self.bot.scheduler.shutdown()
        
        await self.bot.close()
    
    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('meta')
    

def setup(bot: Bot):
    bot.add_cog(Meta(bot))
