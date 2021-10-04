from datetime import datetime
from typing import Union

from discord.ext.commands import Cog
from discord import Reaction, Member, User, RawReactionActionEvent, Message, Embed

from lib.bot import Bot
from lib.db import db


class Reactions(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
            
    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.colours = {
                '❤️': self.bot.guild.get_role(893962799410196531), # Red
                '💛': self.bot.guild.get_role(893963069208789012), # Yellow
                '💚': self.bot.guild.get_role(893963180970217502), # Green
                '💙': self.bot.guild.get_role(893963509723975720), # Blue
                '💜': self.bot.guild.get_role(893963613914685551), # Purple
                '🖤': self.bot.guild.get_role(893963674081976320), # Black
            }
            
            self.reaction_message: Message = await self.bot.get_channel(825080559369846789).fetch_message(893958842935803914)
            self.starboard_channel = self.bot.get_channel(894351653682163743)
            assert self.reaction_message.content == 'React to get a colour!'
            self.bot.cogs_ready.ready_up('reactions')
    
    # @Cog.listener()
    # async def on_reaction_add(self, reaction: Reaction, user: Union[Member, User]):
    #     print(f'{user.display_name} reacted with {reaction.emoji}. Event type: regular.')
    
    # @Cog.listener()
    # async def on_reaction_remove(self, reaction: Reaction, user: Union[Member, User]):
    #     print(f'{user.display_name} removed reaction {reaction.emoji}. Event type: regular.')

    @Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        if payload.message_id == self.reaction_message.id:
            current_colours = filter(lambda r: r in self.colours.values(), payload.member.roles)
            await payload.member.remove_roles(*current_colours)
            await payload.member.add_roles(self.colours[payload.emoji.name])
            await self.reaction_message.remove_reaction(payload.emoji, payload.member)
        elif payload.emoji.name == '⭐':
            message: Message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
                        
            if not message.author.bot: # and payload.member.id != message.author.id:
                sql_query = 'SELECT StarMessageID, Stars FROM starboard WHERE RootMessageID = ?'
                sql_data = message.id
                msg_id, stars = db.record(sql_query, sql_data) or (None, 0)
                
                embed = Embed(title='Starred message',
                              colour=message.author.colour,
                              timestamp=datetime.utcnow())
                
                embed.add_field(name='Author', value=message.author.mention, inline=False)
                embed.add_field(name='Content', value=message.content or 'See attachment.', inline=False)
                embed.add_field(name='Stars', value=stars+1, inline=False)
                
                if len(message.attachments):
                    embed.set_image(url=message.attachments[0].url)
                
                if stars == 0:
                    star_message = await self.starboard_channel.send(embed=embed)
                    sql_query = 'INSERT INTO starboard (RootMessageID, StarMessageID) VALUES (?, ?)'
                    sql_data = (message.id, star_message.id)
                    db.execute(sql_query, *sql_data)
                    db.commit()
                else:
                    star_message = await self.starboard_channel.fetch_message(msg_id)
                    await star_message.edit(embed=embed)
                    
                    sql_query = 'UPDATE starboard SET Stars = Stars + 1 WHERE RootMessageID = ?'
                    sql_data = message.id
                    db.execute(sql_query, sql_data)
                    db.commit()
            else:
                await message.remove_reaction(payload.emoji, payload.member)

    # @Cog.listener()
    # async def on_raw_reaction_remove(self, payload: RawReactionActionEvent):
    #     if payload.message_id == self.reaction_message.id:
    #         member = self.bot.guild.get_member(payload.user_id)
    #         role = self.bot.guild.get_role(colours.get(payload.emoji.name))
    #         await member.remove_roles(role)

                
def setup(bot: Bot):
    bot.add_cog(Reactions(bot))
