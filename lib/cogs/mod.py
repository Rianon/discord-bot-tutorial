from datetime import datetime, timedelta
from typing import List, Optional, Union
from asyncio import sleep
import pytz

from discord import Member, TextChannel, Embed, Role, NotFound, Object
from discord.utils import find
from discord.ext.commands import (Cog, Context, Converter,
                                  Greedy,
                                  command, has_permissions, bot_has_permissions)
from discord.ext.commands.errors import MissingPermissions, BotMissingPermissions, BadArgument

from lib.bot import Bot
from lib.db import db


class BannedUser(Converter):
	async def convert(self, ctx: Context, arg: Union[int, str]):
		if ctx.guild.me.guild_permissions.ban_members:
			if arg.isdigit():
				try:
					return (await ctx.guild.fetch_ban(Object(id=int(arg)))).user
				except NotFound:
					raise BadArgument

		banned = [e.user for e in await ctx.guild.bans()]
		if banned:
			if (user := find(lambda u: str(u) == arg, banned)) is not None:
				return user
			else:
				raise BadArgument


class Mod(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        self.log_channel: TextChannel = self.bot.get_channel(825090188619022356)
        self.mute_role: Role = self.bot.guild.get_role(888124084486041600)
        
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('mod')
    
    @command(name='kick', brief='Kicks user from server.')
    @bot_has_permissions(kick_members=True)
    @has_permissions(kick_members=True)
    async def kick_member(self, ctx: Context, targets: Greedy[Member], *, reason: Optional[str] = 'No reason provided.'):
        """Kicks provided user(s) from server."""
        await ctx.message.delete()
        
        if not len(targets):
            await ctx.send('One or more required arguments were missed.')
        else:
            for target in targets:
                if (ctx.guild.me.top_role.position > target.top_role.position
                    and not target.guild_permissions.administrator):
                    await target.kick(reason=reason)
                    embed = Embed(title=f'Member {target} has been kicked from server',
                                colour=0xFF0000,
                                timestamp=datetime.utcnow())
                    
                    embed.add_field(name='Reason', value=reason, inline=False)
                    embed.add_field(name='Moderator', value=ctx.author.mention, inline=False)
                    embed.set_thumbnail(url=target.avatar_url)
                    
                    await ctx.send(embed=embed)
                    print(f'[SUCCESS] {target} has been kicked from server. Reason: {reason}')
    
    @kick_member.error
    async def kick_member_error(self, ctx: Context, error):
        if isinstance(error, MissingPermissions):
            await ctx.send('Action forbidden, you have no **<kick members>** permission.')
        elif isinstance(ctx, BotMissingPermissions):
            await ctx.send('Action forbidden, this bot has no **<kick members>** permission.')

    @command(name='ban', brief='Bans user from server.')
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def ban_member(self, ctx: Context, targets: Greedy[Member], *, reason: Optional[str] = 'No reason provided.'):
        """Bans provided user(s) from server."""
        await ctx.message.delete()
        
        if not len(targets):
            await ctx.send('One or more required arguments are missing.')
        else:
            for target in targets:
                if (ctx.guild.me.top_role.position > target.top_role.position
                    and not target.guild_permissions.administrator):
                    await target.ban(reason=reason)
                    embed = Embed(title=f'Member {target} has been banned from server',
                                colour=0xFF0000,
                                timestamp=datetime.utcnow())
                    
                    embed.add_field(name='Reason', value=reason, inline=False)
                    embed.add_field(name='Moderator', value=ctx.author.mention, inline=False)
                    embed.set_thumbnail(url=target.avatar_url)
                    
                    await ctx.send(embed=embed)
                    print(f'[SUCCESS] {target} has been banned from server. Reason: {reason}')
    
    @ban_member.error
    async def ban_member_error(self, ctx: Context, error):
        if isinstance(error, MissingPermissions):
            await ctx.send('Action forbidden, **<ban members>** permission needed.')
        elif isinstance(ctx, BotMissingPermissions):
            await ctx.send('Action forbidden, this bot has no **<ban members>** permission.')
    
    @command(name="unban", brief='Unbans the user.')
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def unban(self, ctx: Context, targets: Greedy[BannedUser], *, reason: Optional[str] = 'No reason provided.'):
        """Unbans the provided user(s) by their name or ID."""
        if not len(targets):
            await ctx.send('One or more required arguments are missing.')
        else:
            for target in targets:
                await ctx.guild.unban(target, reason=reason)

                embed = Embed(title=f'Member {target} has been unbanned',
                                colour=0x00FF00,
                                timestamp=datetime.utcnow())

                embed.set_thumbnail(url=target.avatar_url)
                embed.add_field(name='Reason', value=reason, inline=False)
                embed.add_field(name='Moderator', value=ctx.author.mention, inline=False)

                await ctx.send(embed=embed)
    
    @command(name='mute', brief='Mutes the user.')
    @has_permissions(manage_roles=True, manage_guild=True)
    @bot_has_permissions(manage_roles=True)
    async def mute_member(self, ctx: Context, targets: Greedy[Member], hours: Optional[int], *, reason: Optional[str] = 'No reason provided.'):
        """Mutes the provided user(s) for provided duration."""
        if not len(targets):
            await ctx.send('One or more required arguments are missing.')
        else:
            unmutes = []
            
            for target in targets:
                if not self.mute_role in target.roles:
                    if ctx.guild.me.top_role.position > target.top_role.position:
                        role_ids = ','.join([str(r.id) for r in target.roles])
                        end_time = datetime.utcnow() + timedelta(seconds=hours) if hours else None
                        
                        sql_query = 'INSERT INTO mutes VALUES (?, ?, ?)'
                        sql_data = (target.id, role_ids, getattr(end_time, 'isoformat', lambda: None)())
                        db.execute(sql_query, *sql_data)
                        db.commit()
                        
                        await target.edit(roles=[self.mute_role])
                        
                        embed = Embed(title=f'Member {target} muted',
                                colour=0xFF0000)
                    
                        embed.add_field(name='Reason', value=reason, inline=False)
                        mute_duration = f'{hours:,}h' if hours else 'Indefinite'
                        embed.add_field(name='Duration', value=mute_duration, inline=False)
                        embed.add_field(name='Moderator', value=ctx.author.mention, inline=False)
                        embed.set_thumbnail(url=target.avatar_url)
                        # expires_time = pytz.timezone('Europe/Moscow').fromutc(end_time) if end_time else 'Never'
                        embed.timestamp = end_time or Embed.Empty
                        if end_time:
                            embed.set_footer(text=f'Expires: ')
                        else:
                            embed.set_footer(text=f'Expires: Never')
                        
                        await ctx.send(embed=embed)
                        print(f'[SUCCESS] {target} has been muted. Duration: {mute_duration}')
                        
                        if hours:
                            unmutes.append(target)
                    else:
                        await ctx.send(f'{target} could not be muted.')
                else:
                    await ctx.send(f'Action not needed, {target} is already muted.')
            
            if len(unmutes):
                await sleep(hours)
                await self.unmute(ctx, targets)
    
    @mute_member.error
    async def mute_member_error(self, ctx: Context, error):
        if isinstance(error, MissingPermissions):
            await ctx.send('Action forbidden, **<manage roles>** and **<manage server>** permissions needed.')
        elif isinstance(ctx, BotMissingPermissions):
            await ctx.send('Action forbidden, this bot has no **<manage roles>** permission.')
    
    async def unmute(self, ctx: Context, targets: List[Member], *, reason='Mute has expired.' ):
        for target in targets:
            if self.mute_role in target.roles:
                sql_query = 'SELECT RolesIDs FROM mutes WHERE UserID = ?'
                sql_data = target.id
                role_ids = db.field(sql_query, sql_data)
                roles = [ctx.guild.get_role(int(id_)) for id_ in role_ids.split(',') if len(id_)]
                
                sql_query = 'DELETE FROM mutes WHERE UserID = ?'
                sql_data = target.id
                db.execute(sql_query, sql_data)
                db.commit()
                
                await target.edit(roles=roles)
                
                embed = Embed(title=f'Member {target} unmuted',
                                colour=0x00FF00,
                                timestamp=datetime.utcnow())
                    
                embed.add_field(name='Reason', value=reason, inline=False)
                embed.set_thumbnail(url=target.avatar_url)
                
                await ctx.send(embed=embed)
                print(f'[SUCCESS] {target} has been unmuted.')
            else:
                await ctx.send(f'Action not needed, member {target.mention} is not muted.')
    
    @command(name='unmute', brief='Unmutes the user.')
    @has_permissions(manage_roles=True, manage_guild=True)
    @bot_has_permissions(manage_roles=True)
    async def unmute_member(self, ctx: Context, targets: Greedy[Member], *, reason: Optional[str] = 'No reason provided.'):
        """Unmutes the provided user(s)."""
        if not len(targets):
            await ctx.send('One or more required arguments are missing.')
        else:
            await self.unmute(ctx, targets, reason=reason)
        
    @unmute_member.error
    async def mute_member_error(self, ctx: Context, error):
        if isinstance(error, MissingPermissions):
            await ctx.send('Action forbidden, **<manage roles>** and **<manage server>** permissions needed.')
        elif isinstance(ctx, BotMissingPermissions):
            await ctx.send('Action forbidden, this bot has no **<manage roles>** permission.')


def setup(bot: Bot):
    bot.add_cog(Mod(bot))
