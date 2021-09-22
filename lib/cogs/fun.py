import discord
from typing import Optional, Union
from discord.ext.commands import Cog, Context, command
from discord import Member, Role, Embed
from random import randint
from aiohttp import request
from datetime import datetime

from lib.bot import Bot


class Fun(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('fun')

    @command(name='hello', aliases=['hi'])
    async def __say_hello(self, ctx: Context):
        """Says hello to user."""
        ctx.message.delete()
        author: Member = ctx.author
        await ctx.send(f'Hello, {author.mention}')

    @command(name='dice', aliases=['roll'])
    async def roll_dice(self, ctx: Context, dice_string: str):
        """Rolling specified number of dice."""
        ctx.message.delete()
        dice, value = dice_string.split('d')
        rolls = [str(randint(1, int(value))) for _ in range(int(dice))]
        sum_rolls = sum([int(term) for term in rolls])
        await ctx.send(f'`{", ".join(rolls)} = {sum_rolls}`')

    @roll_dice.error
    async def roll_dice_error(self, ctx: Context, error):
        if isinstance(error.original, discord.errors.HTTPException):
            await ctx.send('Result is too large. Try rolling less dice.')

    @command(name='slap', aliases=['hit'])
    async def __slap(self, ctx: Context, member: Union[Member, Role], *, reason: Optional[str] = 'no reason'):
        """Slaps specified user."""
        ctx.message.delete()
        author: Member = ctx.author
        await ctx.send(f'{author.mention} slapped {member.mention} for {reason}.')
        
    @command(name='fact')
    async def __animal_fact(self, ctx: Context, animal: str = 'cat'):
        """Tells a random fact about specified animal. Default is a cat."""
        if animal.lower() in ('dog', 'cat', 'panda', 'fox', 'koala', 'bird', 'racoon', 'kangaroo'):
            URL = f'https://some-random-api.ml/animal/{animal.lower()}'
            async with request('GET', URL) as response:
                if response.status == 200:
                    data = await response.json()
                    embed = Embed(title=f'**{animal.upper()}**', colour=0x00FF00)
                    embed.add_field(name=f'A random {animal.lower()} fact:', value=data['fact'])
                    embed.set_image(url=data['image'])
                    embed.timestamp = datetime.utcnow()
                    embed.set_footer(text='Source: https://some-random-api.ml', icon_url='https://i.some-random-api.ml/logo.png')
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f'API returned status: {response.status}')
        else:
            await ctx.send('We have no facts on this animal right now. May be later.')


def setup(bot: Bot):
    bot.add_cog(Fun(bot))
