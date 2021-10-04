from datetime import datetime, timedelta
from typing import Union

from discord.ext.commands import Cog, command, has_permissions, Context
from discord import Reaction, Member, User, RawReactionActionEvent, Message, Embed

from lib.bot import Bot
from lib.db import db


numbers = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

class Reactions(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.polls = []
            
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
            # assert self.reaction_message.content == 'React to get a colour!'
            self.bot.cogs_ready.ready_up('reactions')
    
    @command(name='createpoll', aliases=['mkpoll'], brief='Creates a poll.')
    @has_permissions(manage_guild=True)
    async def create_poll(self, ctx: Context, hours: int, question: str, *options):
        """Creates a poll."""
        if len(options) > 10:
            await ctx.send('You can only supply a maximum of 10 options.')
        else:
            embed = Embed(title='Poll',
                        description=question,
                        colour=ctx.author.colour,
                        timestamp=datetime.utcnow())
                            
            embed.add_field(name='Options', value='\n'.join([f"{numbers[idx]} {option}" for idx, option in enumerate(options)]), inline=False)
            embed.add_field(name='Instructions', value='React to cast a vote!', inline=False)
            
            message = await ctx.send(embed=embed)
            
            for emoji in numbers[:len(options)]:
                await message.add_reaction(emoji)
            
            self.polls.append((message.channel.id, message.id))
            
            self.bot.scheduler.add_job(self.complete_poll, trigger='date', run_date=datetime.now()+timedelta(seconds=hours),
                                       args=[message.channel.id, message.id])

    async def complete_poll(self, channel_id, message_id):
	    message: Message = await self.bot.get_channel(channel_id).fetch_message(message_id)

	    most_voted: Reaction = max(message.reactions, key=lambda r: r.count)

	    await message.channel.send(f"The results are in and option {most_voted.emoji} was the most popular with {most_voted.count-1:,} votes!")
	    self.polls.remove((message.channel.id, message.id))
    
    @Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        if payload.message_id == self.reaction_message.id:
            current_colours = filter(lambda r: r in self.colours.values(), payload.member.roles)
            await payload.member.remove_roles(*current_colours)
            await payload.member.add_roles(self.colours[payload.emoji.name])
            await self.reaction_message.remove_reaction(payload.emoji, payload.member)
        
        elif payload.message_id in (poll[1] for poll in self.polls):
            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

            for reaction in message.reactions:
                if (not payload.member.bot
					and payload.member in await reaction.users().flatten()
					and reaction.emoji != payload.emoji.name):
                    await message.remove_reaction(reaction.emoji, payload.member)
        
        elif payload.emoji.name == '⭐':
            message: Message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
                        
            if not message.author.bot and payload.member.id != message.author.id:
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
