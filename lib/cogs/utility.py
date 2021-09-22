import discord
from discord.ext.commands import Cog, Context, command
from lib.bot import Bot

class Utility(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
    
    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('utility')
    
    @command(name='clear', aliases=['cl'])
    async def __clear_message(self, ctx: Context, amount: int = 10):
        """Clears specified number of messages. Default is 10."""
        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=amount)
        embed = discord.Embed(title=f'{len(deleted)} message(s) has been deleted.', color=0x00FF00)
        await ctx.send(embed=embed, delete_after=5)
        print(f'[SUCCESS] {len(deleted)} message(s) has been deleted.')
        

def setup(bot: Bot):
    bot.add_cog(Utility(bot))
