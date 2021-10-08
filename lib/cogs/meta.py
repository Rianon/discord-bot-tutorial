from email import message
from apscheduler.triggers.cron import CronTrigger
from discord import Activity, ActivityType
from discord.ext.commands import Cog, Context, command

from lib.bot import Bot
from lib.db import db

class Meta(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self._message = 'watching {prefix}help | {users:,} user(s) in {guilds:,} server(s).'
        bot.scheduler.add_job(self.set, CronTrigger(second=0))
    
    @property
    def message(self):
        sql_query = 'SELECT Prefix FROM guilds WHERE GuildID = ?'
        _prefix: str = db.field(sql_query, self.bot.guild.id)
        print(f'Prefix set to: {_prefix}')
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
    
    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('meta')
    

def setup(bot: Bot):
    bot.add_cog(Meta(bot))
