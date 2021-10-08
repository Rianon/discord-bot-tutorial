from asyncio import sleep
from datetime import datetime, timedelta
from re import search
from typing import Optional, Union

from better_profanity import profanity
from discord import Embed, Member, Message, NotFound, Object, Role, TextChannel
from discord.ext.commands import (Cog, Context, Converter, Greedy,
                                  bot_has_permissions, command,
                                  has_permissions)
from discord.ext.commands.errors import (BadArgument, BotMissingPermissions,
                                         MissingPermissions)
from discord.utils import find
from lib.bot import Bot
from lib.db import db

# import pytz

profanity.load_censor_words_from_file('./data/profanity.txt')
# profanity.load_censor_words()

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
        self.url_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        self.allow_links = ('892892601202663464') # let allow link posting to, say, links channel only
        self.allow_images = ('892892601202663464') # same channel, for images

    @Cog.listener()
    async def on_ready(self):
        self.log_channel: TextChannel = self.bot.get_channel(825090188619022356) # set log channel
        self.mute_role: Role = self.bot.guild.get_role(888124084486041600) # set mute role
        
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('mod')
    
    @Cog.listener()
    async def on_message(self, message: Message):
        # if message author is the same as earlier and used mentions and an interval between messages is less then 1 minute
        def _check(m: Message):
            return(m.author == message.author
                   and len(m.mentions)
                   and (datetime.utcnow() - m.created_at).seconds < 60)
        
        if not message.author.bot:
            current_prefix = await self.bot.get_prefix(message)
            if isinstance(current_prefix, list):
                current_prefix = current_prefix[-1]
            if not str(message.content).startswith(str(current_prefix)):
                msg_to_check = list(self.bot.cached_messages)[-10:]
                if len(list(filter(lambda m: _check(m), msg_to_check))) >= 3:
                    msg = await message.channel.send(f'**{message.author.mention}** spaming mentions, huh? How disappointing.', delete_after=5)
                    await self.kick_members(msg, [message.author], 'Mentions spam.')
                
                if profanity.contains_profanity(message.content):
                    await message.delete()
                    await message.channel.send("You can't use that word here.", delete_after=5)
                elif str(message.channel.id) not in self.allow_links and search(self.url_regex, message.content):
                    await message.delete()
                    await message.channel.send("You can't post links here.", delete_after=5)
                if str(message.channel.id) not in self.allow_images and any([hasattr(a, 'width') for a in message.attachments]):
                    await message.delete()
                    await message.channel.send("You can't post images here.", delete_after=5)
    
    # Kick function
    async def kick_members(self, message: Message, targets, reason):
        for target in targets:
            if (message.guild.me.top_role.position > target.top_role.position
                and not target.guild_permissions.administrator):
                await target.kick(reason=reason)
                embed = Embed(title=f'Member {target} has been kicked from server',
                              colour=0xFF0000,
                              timestamp=datetime.utcnow())
                
                embed.add_field(name='Reason', value=reason, inline=False)
                embed.add_field(name='Moderator', value=message.author.mention, inline=False)
                embed.set_thumbnail(url=target.avatar_url)
                
                await message.channel.send(embed=embed)
                print(f'[SUCCESS] {target} has been kicked from server. Reason: {reason}')
    
    # Kick command
    @command(name='kick', brief='Kicks user from server.')
    @bot_has_permissions(kick_members=True)
    @has_permissions(kick_members=True)
    async def kick_command(self, ctx: Context, targets: Greedy[Member], *, reason: Optional[str] = 'No reason provided.'):
        """Kicks provided user(s) from server."""
        await ctx.message.delete()
        
        if not len(targets):
            await ctx.send('One or more required arguments were missed.')
        else:
            await self.kick_members(ctx.message, targets, reason)
    
    @kick_command.error
    async def kick_member_error(self, ctx: Context, error):
        if isinstance(error, MissingPermissions):
            await ctx.send('Action forbidden, you have no **<kick members>** permission.')
        elif isinstance(ctx, BotMissingPermissions):
            await ctx.send('Action forbidden, this bot has no **<kick members>** permission.')

    # Ban function
    async def ban_members(self, message: Message, targets, reason):
        for target in targets:
            if (message.guild.me.top_role.position > target.top_role.position
                and not target.guild_permissions.administrator):
                await target.ban(reason=reason)
                embed = Embed(title=f'Member {target} has been banned from server',
                              colour=0xFF0000,
                              timestamp=datetime.utcnow())
                
                embed.add_field(name='Reason', value=reason, inline=False)
                embed.add_field(name='Moderator', value=message.author.mention, inline=False)
                embed.set_thumbnail(url=target.avatar_url)
                
                await message.channel.send(embed=embed)
                print(f'[SUCCESS] {target} has been banned from server. Reason: {reason}')

    # Ban command
    @command(name='ban', brief='Bans user from server.')
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def ban_command(self, ctx: Context, targets: Greedy[Member], *, reason: Optional[str] = 'No reason provided.'):
        """Bans provided user(s) from server."""
        await ctx.message.delete()
        
        if not len(targets):
            await ctx.send('One or more required arguments are missing.')
        else:
            await self.ban_members(ctx.message, targets, reason)
    
    @ban_command.error
    async def ban_member_error(self, ctx: Context, error):
        if isinstance(error, MissingPermissions):
            await ctx.send('Action forbidden, **<ban members>** permission needed.')
        elif isinstance(ctx, BotMissingPermissions):
            await ctx.send('Action forbidden, this bot has no **<ban members>** permission.')
    
    # Unban command
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
    
    # Mute function
    async def mute_members(self, message: Message, targets, hours, reason):
        unmutes = []
            
        for target in targets:
            if not self.mute_role in target.roles:
                if message.guild.me.top_role.position > target.top_role.position:
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
                    embed.add_field(name='Moderator', value=message.author.mention, inline=False)
                    embed.set_thumbnail(url=target.avatar_url)
                    # expires_time = pytz.timezone('Europe/Moscow').fromutc(end_time) if end_time else 'Never'
                    embed.timestamp = end_time or Embed.Empty
                    if end_time:
                        embed.set_footer(text=f'Expires: ')
                    else:
                        embed.set_footer(text=f'Expires: Never')
                    
                    await message.channel.send(embed=embed)
                    print(f'[SUCCESS] {target} has been muted. Duration: {mute_duration}')
                    
                    if hours:
                        unmutes.append(target)
            else:
                await message.channel.send(f'Action not needed, {target.mention} is already muted.')
                    
        return unmutes
    
    # Mute command
    @command(name='mute', brief='Mutes the user.')
    @has_permissions(manage_roles=True, manage_guild=True)
    @bot_has_permissions(manage_roles=True)
    async def mute_command(self, ctx: Context, targets: Greedy[Member], hours: Optional[int], *, reason: Optional[str] = 'No reason provided.'):
        """Mutes the provided user(s) for provided duration."""
        if not len(targets):
            await ctx.send('One or more required arguments are missing.')
        else:
            unmutes = self.mute_members(ctx.message, targets, hours, reason)
            if len(unmutes):
                await sleep(hours)
                await self.unmute(ctx.message, targets)
    
    @mute_command.error
    async def mute_member_error(self, ctx: Context, error):
        if isinstance(error, MissingPermissions):
            await ctx.send('Action forbidden, **<manage roles>** and **<manage server>** permissions needed.')
        elif isinstance(ctx, BotMissingPermissions):
            await ctx.send('Action forbidden, this bot has no **<manage roles>** permission.')
    
    # Unmute function
    async def unmute(self, message: Message, targets, reason='Mute has expired.' ):
        for target in targets:
            if self.mute_role in target.roles:
                sql_query = 'SELECT RolesIDs FROM mutes WHERE UserID = ?'
                sql_data = target.id
                role_ids: str = db.field(sql_query, sql_data)
                roles = [message.guild.get_role(int(id_)) for id_ in role_ids.split(',') if len(id_)]
                
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
                
                await message.channel.send(embed=embed)
                print(f'[SUCCESS] {target} has been unmuted.')
            else:
                await message.channel.send(f'Action not needed, member {target.mention} is not muted.')
    
    # Unmute command
    @command(name='unmute', brief='Unmutes the user.')
    @has_permissions(manage_roles=True, manage_guild=True)
    @bot_has_permissions(manage_roles=True)
    async def unmute_command(self, ctx: Context, targets: Greedy[Member], *, reason: Optional[str] = 'No reason provided.'):
        """Unmutes the provided user(s)."""
        if not len(targets):
            await ctx.send('One or more required arguments are missing.')
        else:
            await self.unmute(ctx.message, targets, reason)
        
    @unmute_command.error
    async def mute_member_error(self, ctx: Context, error):
        if isinstance(error, MissingPermissions):
            await ctx.send('Action forbidden, **<manage roles>** and **<manage server>** permissions needed.')
        elif isinstance(ctx, BotMissingPermissions):
            await ctx.send('Action forbidden, this bot has no **<manage roles>** permission.')
    
    # Addprofanity command
    @command(name='addprofanity', aliases=['as', 'ac'], brief='Add words to profanity filter.')
    @has_permissions(manage_guild=True)
    async def add_profanity(self, ctx: Context, *words):
        """Add words to profanity filter."""
        if ctx.message:
            await ctx.message.delete()
        
        profanity.add_censor_words(words)
        with open('./data/profanity.txt', 'a', encoding='utf-8') as f:
            f.write(''.join([f'{w}\n' for w in words]))
        
        embed = Embed(title='Profanity filter updated.',
                      color=0x00FF00)
                
        await ctx.send(embed=embed, delete_after=5)
        print(f'[SUCCESS] Profanity filter updated.')

    # Removeprofanity command
    @command(name='removeprofanity', aliases=['rs', 'rc'], brief='Remove words from profanity filter.')
    @has_permissions(manage_guild=True)
    async def remove_profanity(self, ctx: Context, *words):
        """Remove words from profanity filter."""
        if ctx.message:
            await ctx.message.delete()
        
        with open('./data/profanity.txt', 'r', encoding='utf-8') as f:
            stored = [w.strip() for w in f.readlines()]
        with open('./data/profanity.txt', 'w', encoding='utf-8') as f:
            f.write(''.join([f'{w}\n' for w in stored if w not in words]))
        
        embed = Embed(title='Profanity filter updated.',
                      color=0x00FF00)
                
        await ctx.send(embed=embed, delete_after=5)
        print(f'[SUCCESS] Profanity filter updated.')


def setup(bot: Bot):
    bot.add_cog(Mod(bot))
