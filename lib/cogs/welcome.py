from discord import Member, Role
from discord.ext.commands import Cog
from discord.errors import Forbidden
from lib.bot import Bot
from lib.db import db


class Welcome(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('welcome')

    @Cog.listener()
    async def on_member_join(self, member: Member):
        sql_query = 'SELECT UserID FROM exp WHERE UserID = ?'
        query_result = db.field(sql_query, member.id)

        if not query_result:
            sql_query = 'INSERT INTO exp (UserID) VALUES (?)'
            db.execute(sql_query, member.id)
            db.commit()

        await self.bot.get_channel(891015145801777222).send(f'Welcome, **{member.mention}**!')

        try:
            await member.send(f'Welcome to **{member.guild.name}**!')
        except Forbidden:
            pass

        role_to_add: Role = member.guild.get_role(891017179795972166)
        await member.add_roles(role_to_add, reason='Joined to server.')

    @Cog.listener()
    async def on_member_remove(self, member: Member):
        sql_query = 'SELECT UserID FROM exp WHERE UserID = ?'
        query_result = db.field(sql_query, member.id)

        if query_result:
            sql_query = 'DELETE FROM exp WHERE UserID = ?'
            db.execute(sql_query, member.id)
            db.commit()

        await self.bot.get_channel(891015145801777222).send(f'{member.display_name} has left server.')


def setup(bot: Bot):
    bot.add_cog(Welcome(bot))
