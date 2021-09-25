from datetime import datetime
from typing import Optional

from discord import Member, TextChannel, Embed
from discord.ext.commands import Cog, Context, command, Greedy, has_permissions, bot_has_permissions
from discord.ext.commands.errors import MissingPermissions, BotMissingPermissions

from lib.bot import Bot


class Mod(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        self.log_channel: TextChannel = self.bot.get_channel(825090188619022356)
        
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('mod')
    
    @command(name='kick', brief='Kicks user from server.')
    @bot_has_permissions(kick_members=True)
    @has_permissions(kick_members=True)
    async def __kick_member(self, ctx: Context, targets: Greedy[Member], *, reason: Optional[str] = 'No reason provided.'):
        """Kicks user from server."""
        await ctx.message.delete()
        
        if not len(targets):
            await ctx.send('One or more required arguments were missed.')
        else:
            for target in targets:
                await target.kick(reason=reason)
                embed = Embed(title='Member kicked',
                              colour=0xFF0000,
                              timestamp=datetime.utcnow())
                
                embed.add_field(name='Name', value=f'{target.mention}', inline=False)
                embed.add_field(name='Reason', value=reason, inline=False)
                embed.set_thumbnail(url=target.avatar_url)
                embed.set_footer(text=f'Kicked by {ctx.author.display_name}')
                
                await ctx.send(embed=embed)
                print(f'[SUCCESS] {target} has been kicked from server.')
    
    @__kick_member.error
    async def kick_member_error(self, ctx: Context, error):
        if isinstance(error, MissingPermissions):
            await ctx.send('Action forbidden, you have no **<kick members>** permission.')
        elif isinstance(ctx, BotMissingPermissions):
            await ctx.send('Action forbidden, this bot has no **<kick members>** permission.')

    @command(name='ban', brief='Bans user from server.')
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def __ban_member(self, ctx: Context, targets: Greedy[Member], *, reason: Optional[str] = 'No reason provided.'):
        """Bans user from server."""
        await ctx.message.delete()
        
        if not len(targets):
            await ctx.send('One or more required arguments were missed.')
        else:
            for target in targets:
                await target.ban(reason=reason)
                embed = Embed(title='Member banned',
                              colour=0xFF0000,
                              timestamp=datetime.utcnow())
                
                embed.add_field(name='Name', value=f'{target.mention}', inline=False)
                embed.add_field(name='Reason', value=reason, inline=False)
                embed.set_thumbnail(url=target.avatar_url)
                embed.set_footer(text=f'Banned by {ctx.author.display_name}')
                
                await ctx.send(embed=embed)
                print(f'[SUCCESS] {target} has been banned from server.')
    
    @__ban_member.error
    async def ban_member_error(self, ctx: Context, error):
        if isinstance(error, MissingPermissions):
            await ctx.send('Action forbidden, you have no **<ban members>** permission.')
        elif isinstance(ctx, BotMissingPermissions):
            await ctx.send('Action forbidden, this bot has no **<ban members>** permission.')


def setup(bot: Bot):
    bot.add_cog(Mod(bot))
