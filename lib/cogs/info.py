from typing import Optional

from datetime import datetime

from discord import Member, Embed
from discord.ext.commands import (Cog, Context,
                                  command)

from lib.bot import Bot


class Info(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('info')
    
    @command(name='userinfo', aliases=['ui', 'mi', 'member info'], brief='Shows user info.')
    async def show_user_info(self, ctx: Context, target: Optional[Member]):
        """Shows user info."""
        await ctx.message.delete()
        
        target = target or ctx.author
        
        embed = Embed(title='User information',
                      colour=target.colour,
                      timestamp=datetime.utcnow())
        
        embed.add_field(name='Name', value=str(target), inline=True)
        embed.add_field(name='ID', value=target.id, inline=True)
        embed.add_field(name='Bot?', value=target.bot, inline=True)
        embed.add_field(name='Top role', value=target.top_role.mention, inline=True)
        embed.add_field(name='Status', value=str(target.status).title(), inline=True)
        
        if target.activity:
            value = f'{str(target.activity.type).split(".")[-1].title()} {target.activity.name}'
        else:
            value = 'None'
        
        embed.add_field(name='Activity', value=value, inline=True)
        embed.add_field(name='Created at', value=target.created_at.strftime('%d/%m/%Y %H:%M:%S'), inline=True)
        embed.add_field(name='Joined at', value=target.joined_at.strftime('%d/%m/%Y %H:%M:%S'), inline=True)
        embed.add_field(name='Boosted', value=bool(target.premium_since), inline=True)
        embed.set_thumbnail(url=target.avatar_url)
        
        await ctx.send(embed=embed)
    
    @command(name='serverinfo', aliases=['si', 'gi', 'guildinfo'], brief='Shows server info.')
    async def show_server_info(self, ctx: Context):
        """Shows server info."""
        await ctx.message.delete()
        
        embed = Embed(title='Server information',
                      colour=ctx.guild.owner.colour,
                      timestamp=datetime.utcnow())
        
        statuses = [len(list(filter(lambda m: str(m.status) == 'online', ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == 'idle', ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == 'dnd', ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == 'offline', ctx.guild.members)))
                    ]
        
        embed.add_field(name='ID', value=ctx.guild.id, inline=True)
        embed.add_field(name='Owner', value=ctx.guild.owner, inline=True)
        embed.add_field(name='Region', value=str(ctx.guild.region).title(), inline=True)
        embed.add_field(name='Created at', value=ctx.guild.created_at.strftime('%d/%m/%Y %H:%M:%S'), inline=True)
        embed.add_field(name='Members', value=len(ctx.guild.members), inline=True)
        embed.add_field(name='Humans', value=len(list(filter(lambda m: not m.bot, ctx.guild.members))), inline=True)
        embed.add_field(name='Bots', value=len(list(filter(lambda m: m.bot, ctx.guild.members))), inline=True)
        embed.add_field(name='Banned members', value=len(await ctx.guild.bans()), inline=True)
        embed.add_field(name='Statuses', value=f'🟢 {statuses[0]} 🟡 {statuses[1]} 🔴 {statuses[2]} ⚪ {statuses[3]}', inline=True)
        embed.add_field(name='Text channels', value=len(ctx.guild.text_channels), inline=True)
        embed.add_field(name='Voice channels', value=len(ctx.guild.voice_channels), inline=True)
        embed.add_field(name='Categories', value=len(ctx.guild.categories), inline=True)
        embed.add_field(name='Roles', value=len(ctx.guild.roles), inline=True)
        embed.add_field(name='Invites', value=len(await ctx.guild.invites()), inline=True)
        embed.add_field(name='\u200b', value='\u200b', inline=True)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        
        await ctx.send(embed=embed)


def setup(bot: Bot):
    bot.add_cog(Info(bot))
