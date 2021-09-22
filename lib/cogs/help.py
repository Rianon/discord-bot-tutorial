from typing import Optional
from discord.utils import get
from discord import Embed
from discord.ext.commands import Cog, Context, Command, command
from discord.ext.menus import MenuPages, ListPageSource
from lib.bot import Bot

def syntax(command: Command) -> str:
    cmd_and_aliases = '|'.join([str(command), *command.aliases])
    params = []
    for key, value in command.params.items():
        if key not in ('self', 'ctx'):
            params.append(f'[{key}]' if 'Optional' in str(value) else f'<{key}>')
    params = ' '.join(params)
    return f'```{cmd_and_aliases} {params}```'

class HelpMenu(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx
        super().__init__(data, per_page=3)
    
    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page*self.per_page) + 1
        len_data = len(self.entries)
        embed = Embed(title='Help',
                      description='Welcome to the help dialog!',
                      colour=self.ctx.author.colour)
        embed.set_thumbnail(url=self.ctx.guild.me.avatar_url)
        embed.set_footer(text=f'{offset:,} - {min(len_data, (offset + self.per_page - 1)):,} of {len_data:,} commands.')
        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)
        return embed
    
    async def format_page(self, menu, entries):
        fields = []
        for entry in entries:
            fields.append((entry.brief or 'No description', syntax(entry)))
        return await self.write_page(menu, fields)


class Help(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.bot.remove_command('help')
    
    async def cmd_help(self, ctx: Context, command: Command):
        embed = Embed(title=f'Help with `{command}`',
                      description=syntax(command),
                      colour=ctx.author.colour)
        embed.add_field(name='Command description:', value=command.help)
        await ctx.send(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('help')

    @command(name='help', aliases=['h'])
    async def __show_help(self, ctx: Context, cmd: Optional[str]):
        """Shows help on commands."""
        if cmd is None:
            menu = MenuPages(source=HelpMenu(ctx, list(self.bot.commands)),
                             delete_message_after=True,
                             timeout=60.0)
            await menu.start(ctx)
        else:
            if (command := get(self.bot.commands, name=cmd)):
                await self.cmd_help(ctx, command)
            else:
                await ctx.send('This command does not exist.')


def setup(bot: Bot):
    bot.add_cog(Help(bot))
