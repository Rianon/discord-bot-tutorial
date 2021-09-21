from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from discord import Intents, TextChannel
# from discord import Embed, File
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import CommandNotFound

# from datetime import datetime

from lib.db import db

PREFIX = '?'
OWNER_IDS = [341671286415687692]


class Bot (BotBase):
    def __init__(self):
        self.PREFIX = PREFIX
        self.ready = False
        self.guild = None
        self.scheduler = AsyncIOScheduler()

        db.autosave(self.scheduler)

        super().__init__(
            command_prefix=PREFIX,
            owner_ids=OWNER_IDS,
            intents=Intents.all()
        )

    def run(self, version):
        self.VERSION = version

        with open('./lib/bot/token.0', 'r', encoding='utf-8') as tf:
            self.TOKEN = tf.read()

        print('Running bot...')
        super().run(self.TOKEN, reconnect=True)

    async def rules_reminder(self):
        channel: TextChannel = self.get_channel(823649821679681549)
        await channel.send('Remember to adhere the rules! Or else... violence.')

    async def on_connect(self):
        print('Bot connected.')

    async def on_disconnect(self):
        print('Bot disconnected.')

    async def on_error(self, err, *args, **kwargs):
        if err == 'on_command_error':
            args[0].send('Something went wrong here.')
        channel: TextChannel = self.guild.system_channel
        await channel.send('An error occured.')
        raise

    async def on_command_error(self, ctx, exc):
        if isinstance(exc, CommandNotFound):
            await ctx.send('There is no such command.')
        elif hasattr(exc, 'original'):
            raise exc.original
        else:
            raise exc

    async def on_ready(self):
        if not self.ready:
            self.ready = True
            self.guild = self.get_guild(823649821679681546)
            self.scheduler.add_job(self.rules_reminder, CronTrigger(
                day_of_week=0, hour=12, minute=0, second=0))
            self.scheduler.start()
            print('Bot is ready.')

            channel: TextChannel = self.guild.system_channel
            await channel.send('Bot is online!')
            # embed = Embed(title='Now online!',
            #               description='Bot is online now.',
            #               colour=0xFF0000,
            #               timestamp=datetime.utcnow())
            # fields = [('Name.', 'Value.', True),
            #           ('Another name.', 'This is inline field.', True),
            #           ('Final name', 'This is not inline field.', False)
            # ]
            # for name, value, inline in fields:
            #     embed.add_field(name=name, value=value, inline=inline)
            # embed.set_footer(text='This is footer.')
            # embed.set_author(name='Rianon SorrowShine', icon_url=self.guild.icon_url)
            # embed.set_thumbnail(url=self.guild.icon_url)
            # embed.set_image(url=self.guild.icon_url)

            # await channel.send(embed=embed)
            # await channel.send(file=File(fp='/images/ava.png'))
        else:
            print('Bot reconnected.')

    async def on_message(self, message):
        pass


bot = Bot()
