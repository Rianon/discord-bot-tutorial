from discord import Member, Role
from discord.ext.commands import Cog
from discord.errors import Forbidden
from lib.bot import Bot
from lib.db import db


class Welcome(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('welcome')

    @Cog.listener()
    async def on_member_join(self, member: Member):
        sql_query = 'SELECT UserID FROM exp WHERE UserID = ?'
        sql_data = member.id
        query_result = db.field(sql_query, sql_data)

        if not query_result:
            sql_query = 'INSERT INTO exp (UserID) VALUES (?)'
            sql_data = member.id
            db.execute(sql_query, sql_data)
            db.commit()

        await self.bot.get_channel(891015145801777222).send(f'Welcome, {member.mention}! Head over to <#823649821679681549> to say hi.')

        try:
            await member.send(f'Welcome to **{member.guild.name}**!')
        except Forbidden:
            pass

        role_to_add: Role = member.guild.get_role(891017179795972166)
        await member.add_roles(role_to_add, reason='Joined to server.')

    @Cog.listener()
    async def on_member_remove(self, member: Member):
        sql_query = 'SELECT UserID FROM exp WHERE UserID = ?'
        sql_data = member.id
        query_result = db.field(sql_query, sql_data)

        if query_result:
            sql_query = 'DELETE FROM exp WHERE UserID = ?'
            sql_data = member.id
            db.execute(sql_query, sql_data)
            db.commit()

        await self.bot.get_channel(891015145801777222).send(f'{member.display_name} has left server.')


def setup(bot: Bot):
    bot.add_cog(Welcome(bot))
