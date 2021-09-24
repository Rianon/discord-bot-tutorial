from discord import Member, TextChannel, Embed, Message, AuditLogAction
from discord.ext.commands import Cog

from datetime import datetime

from lib.bot import Bot

class Log(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
            
    @Cog.listener()
    async def on_ready(self):
        self.log_channel: TextChannel = self.bot.get_channel(825090188619022356)
        
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('log')
    
    @Cog.listener()
    async def on_member_update(self, before: Member, after: Member):
        if not after.bot:
            if before.display_name != after.display_name:
                embed = Embed(title='Member update',
                            description=f'{before.mention} nickname was changed',
                            colour=0x00FF00,
                            timestamp=datetime.utcnow())
                embed.add_field(name='Before:', value=before.display_name)
                embed.add_field(name='After:', value=after.display_name)
                await self.log_channel.send(embed=embed)
            elif before.roles != after.roles:
                embed = Embed(title='Member update',
                            description=f'{before.mention} roles was changed',
                            colour=0x00FF00,
                            timestamp=datetime.utcnow())
                if len(before.roles) > len(after.roles):
                    action = 'Removed '
                    roles = [r for r in before.roles if r not in after.roles]
                else:
                    action = 'Added '
                    roles = [r for r in after.roles if r not in before.roles]
                embed.add_field(name=action, value=', '.join(r.mention for r in roles), inline=False)
                await self.log_channel.send(embed=embed)
    
    @Cog.listener()
    async def on_message_edit(self, before: Message, after: Message):
        if not after.author.bot:
            if before.content != after.content:
                embed = Embed(title=f'Message was edited',
                            colour=0x00FF00,
                            timestamp=datetime.utcnow())
                embed.add_field(name='Before:', value=before.content, inline=False)
                embed.add_field(name='After:', value=after.content, inline=False)
                embed.set_footer(text=f'Edited by {after.author.display_name}')
                await self.log_channel.send(embed=embed)
    
    @Cog.listener()
    async def on_message_delete(self, message: Message):
        if not message.author.bot:
            embed = Embed(title=f'Message was deleted',
                            colour=0x00FF00,
                            timestamp=datetime.utcnow())
            embed.add_field(name='Content:', value=message.content, inline=False)
            # embed.set_footer(text=f'Deleted by {message.author.display_name}')
            # async for entry in self.log_channel.guild.audit_logs(action=AuditLogAction.message_delete, limit=1):
            #     if entry.created_at <= datetime.utcnow():
            #         if entry.target.id == message.author.id:
            #             embed.set_footer(text=f'Deleted by {entry.user.display_name}')
            #         else:
            #             embed.set_footer(text=f'Deleted by {message.author.display_name}')
            await self.log_channel.send(embed=embed)
                
def setup(bot: Bot):
    bot.add_cog(Log(bot))
