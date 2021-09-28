from discord import Embed, Member, Message
from discord.ext.commands import (Cog, Context,
                                  Greedy,
                                  command, has_permissions, bot_has_permissions)
from discord.ext.commands.errors import MissingPermissions

from lib.bot import Bot
from lib.db import db

from typing import Optional
from datetime import datetime, timedelta

class Utility(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('utility')

    @command(name='clear', aliases=['cl', 'purge'], brief='Clears messages in current channel.')
    @has_permissions(manage_messages=True)
    @bot_has_permissions(manage_messages=True, read_message_history=True)
    async def clear_message(self, ctx: Context, targets: Greedy[Member], amount: Optional[int] = 1):
        """Clears provided number of messages (default is 1) from profided list of members in current channel."""
        def _check(message: Message) -> bool:
            return not len(targets) or message.author in targets
        
        if 1 <= amount <= 1000:
            async with ctx.channel.typing():
                await ctx.message.delete()
                deleted = await ctx.channel.purge(limit=amount,
                                                  check=_check,
                                                  after=datetime.utcnow() - timedelta(days=14))
                embed = Embed(title=f'{len(deleted):,} message(s) has been deleted.',
                                    color=0x00FF00)
                
                await ctx.send(embed=embed, delete_after=5)
                print(f'[SUCCESS] {len(deleted)} message(s) has been deleted.')
        else:
            await ctx.send('The amount provided is not within acceptable range. Must be [1 <= N <= 1000].')
    
    @clear_message.error
    async def clear_message_error(self, ctx: Context, error):
        if isinstance(error, MissingPermissions):
            await ctx.send('Action forbidden, **<manage messages>** and **<read_message_history>** permissions needed.')

    @command(name='prefix', aliases=['pre', 'p'], brief='Changes command prefix.')
    @has_permissions(manage_guild=True)
    async def change_prefix(self, ctx: Context, prefix: str):
        """Changes command prefix."""
        if len(prefix) > 5:
            await ctx.send("Prefix can't be longer than 5 characters.")
        else:
            sql_update_query = 'UPDATE guilds SET Prefix = ? WHERE GuildID = ?'
            sql_update_data = (prefix, ctx.guild.id)
            db.execute(sql_update_query, *sql_update_data)
            db.commit()
            await ctx.send(f'Command prefix set to [{prefix}].')

    @change_prefix.error
    async def change_prefix_error(self, ctx: Context, error):
        if isinstance(error, MissingPermissions):
            await ctx.send('Action forbidden, you have no **<manage server>** permission.')


def setup(bot: Bot):
    bot.add_cog(Utility(bot))
