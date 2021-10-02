from typing import Union

from discord.ext.commands import Cog
from discord import Reaction, Member, User, RawReactionActionEvent, Message

from lib.bot import Bot


colours = {
    '❤️': 893962799410196531, # Red
    '💛': 893963069208789012, # Yellow
    '💚': 893963180970217502, # Green
    '💙': 893963509723975720, # Blue
    '💜': 893963613914685551, # Purple
    '🖤': 893963674081976320, # Black
}

class Reactions(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
            
    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.reaction_message: Message = await self.bot.get_channel(825080559369846789).fetch_message(893958842935803914)
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
            role = self.bot.guild.get_role(colours.get(payload.emoji.name))
            await payload.member.add_roles(role)

    @Cog.listener()
    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent):
        if payload.message_id == self.reaction_message.id:
            member = self.bot.guild.get_member(payload.user_id)
            role = self.bot.guild.get_role(colours.get(payload.emoji.name))
            await member.remove_roles(role)

                
def setup(bot: Bot):
    bot.add_cog(Reactions(bot))
