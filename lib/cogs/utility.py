import discord
from discord.ext.commands import Cog, Context, command, has_permissions
from discord.ext.commands.errors import CheckFailure

from lib.bot import Bot
from lib.db import db


class Utility(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('utility')

    @command(name='clear', aliases=['cl'], brief='Clears specified number of messages. Default is 10.')
    async def clear_message(self, ctx: Context, amount: int = 10):
        """Clears specified number of messages. Default is 10."""
        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=amount)
        embed = discord.Embed(
            title=f'{len(deleted)} message(s) has been deleted.', color=0x00FF00)
        await ctx.send(embed=embed, delete_after=5)
        print(f'[SUCCESS] {len(deleted)} message(s) has been deleted.')

    @command(name='prefix', aliases=['pre', 'p'], brief='Changes command prefix.')
    @has_permissions(manage_guild=True)
    async def __change_prefix(self, ctx: Context, prefix: str):
        """Changes command prefix."""
        if len(prefix) > 5:
            await ctx.send("Prefix can't be longer than 5 characters.")
        else:
            sql_update_query = 'UPDATE guilds SET Prefix = ? WHERE GuildID = ?'
            sql_update_data = (prefix, ctx.guild.id)
            db.execute(sql_update_query, *sql_update_data)
            db.commit()
            await ctx.send(f'Command prefix set to [{prefix}].')
    
    @__change_prefix.error
    async def change_prefix_error(self, ctx: Context, error):
        if isinstance(error, CheckFailure):
            await ctx.send('You need the <Manage Server> permission to do this.')


def setup(bot: Bot):
    bot.add_cog(Utility(bot))
