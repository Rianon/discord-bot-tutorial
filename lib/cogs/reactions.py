from typing import Union

from discord.ext.commands import Cog
from discord import Reaction, Member, User, RawReactionActionEvent

from lib.bot import Bot


class Reactions(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
            
    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('reactions')
    
    @Cog.listener()
    async def on_reaction_add(self, reaction: Reaction, user: Union[Member, User]):
        print(f'{user.display_name} reacted with {reaction.emoji}. Event type: regular.')
    
    @Cog.listener()
    async def on_reaction_remove(self, reaction: Reaction, user: Union[Member, User]):
        print(f'{user.display_name} removed reaction {reaction.emoji}. Event type: regular.')

    @Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        print(f'{payload.member.display_name} reacted with {payload.emoji}. Event type: raw.')

    @Cog.listener()
    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent):
        member = self.bot.guild.get_member(payload.user_id)
        print(f'{member.display_name} removed reaction {payload.emoji}. Event type: raw.')

                
def setup(bot: Bot):
    bot.add_cog(Reactions(bot))
