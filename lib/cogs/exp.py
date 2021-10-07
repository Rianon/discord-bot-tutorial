from typing import Optional

from datetime import datetime, timedelta
from random import randint

from discord import Message, Member
from discord.ext.commands import Cog, command, Context

from lib.bot import Bot
from lib.db import db


class Exp(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.xp_delta = 60

    async def process_xp(self, message: Message):
        sql_query = 'SELECT XP, Level, XPLock FROM exp WHERE UserID = ?'
        xp, level, xplock = db.record(sql_query, message.author.id)
        # print(f'From database[exp, {message.author}]: XP={xp}, Level={level}, XPLock={xplock}') # Some debug data
        
        if datetime.utcnow() > datetime.fromisoformat(xplock):
            await self.add_xp(message, xp, level)
    
    async def add_xp(self, message: Message, xp: int, level: int):
        xp_to_add = randint(10, 20)
        new_level = int(((xp + xp_to_add)//42)**0.55)
        # print(f'Added XP={xp_to_add}, new level={new_level}') # Some debug data
        
        sql_query = 'UPDATE exp SET XP = XP + ?, Level = ?, XPLock = ? WHERE UserID = ?'
        xplock = (datetime.utcnow()+timedelta(seconds=self.xp_delta)).isoformat()
        db.execute(sql_query, xp_to_add, new_level, xplock, message.author.id)
        db.commit()
        
        if new_level > level:
            await message.author.send(f'Gratz **{message.author.display_name}** - you reached level **{new_level:,}**!')
    
    @command(name='level', aliases=['lvl', 'lv'], brief='Shows user level.')
    async def show_level(self, ctx: Context, target: Optional[Member]):
        """Shows user level"""
        target = target or ctx.author
        
        sql_query = 'SELECT XP, Level FROM exp WHERE UserID = ?'
        xp, lvl = db.record(sql_query, target.id) or (None, None)
        
        if lvl is not None:
            await ctx.send(f'{target.display_name} is on level {lvl:,} with {xp:,} XP.')
        else:
            await ctx.send("This member can't have a level.")

    @command(name='rank', brief='Shows user rank.')
    async def show_rank(self, ctx: Context, target: Optional[Member]):
        """Shows user rank."""
        target = target or ctx.author
        sql_query = 'SELECT UserID FROM exp ORDER BY XP DESC'
        ids = db.column(sql_query)
        
        try:
            await ctx.send(f'{target.display_name} is rank {ids.index(target.id)+1} of {len(ids)}')
        except ValueError:
            await ctx.send("This member can't have a rank.")
    
    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('exp')

    @Cog.listener()
    async def on_message(self, message: Message):
        if not message.author.bot:
            await self.process_xp(message)


def setup(bot: Bot):
    bot.add_cog(Exp(bot))
