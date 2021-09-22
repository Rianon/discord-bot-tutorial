from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from asyncio import sleep

from discord import Intents, TextChannel, Message
# from discord import Embed, File
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import Context, CommandNotFound, BadArgument, MissingRequiredArgument
from discord.errors import HTTPException, Forbidden

# from datetime import datetime
from glob import glob

from lib.db import db

PREFIX = '?'
OWNER_IDS = [341671286415687692]
COGS = [path.split('\\')[-1][:-3] for path in glob('./lib/cogs/*.py')]
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)


class Ready(object):
    def __init__(self) -> None:
        for cog in COGS:
            setattr(self, cog, False)
    
    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f'[INFO] {cog} cog ready.')
    
    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])

class Bot (BotBase):
    def __init__(self):
        self.PREFIX = PREFIX
        self.ready = False
        self.cogs_ready = Ready()
        self.guild = None
        self.scheduler = AsyncIOScheduler()

        db.autosave(self.scheduler)

        super().__init__(
            command_prefix=PREFIX,
            owner_ids=OWNER_IDS,
            intents=Intents.all()
        )
    
    def setup(self):
        for cog in COGS:
            self.load_extension(f'lib.cogs.{cog}')
            print(f'[SUCCESS] {cog} cog loaded.')

    def run(self, version):
        self.VERSION = version

        print('[INFO] Setting up cogs...')
        self.setup()
        
        with open('./lib/bot/token.0', 'r', encoding='utf-8') as tf:
            self.TOKEN = tf.read()

        print('[INFO] Running bot...')
        super().run(self.TOKEN, reconnect=True)

    async def rules_reminder(self):
        channel: TextChannel = self.get_channel(823649821679681549)
        await channel.send('Remember to adhere the rules! Or else... VIOLENCE.')

    async def on_connect(self):
        print('[INFO] Bot connected.')

    async def on_disconnect(self):
        print('[INFO] Bot disconnected.')

    async def on_error(self, err, *args, **kwargs):
        if err == 'on_command_error':
            await args[0].send('Something went wrong here.')
        raise

    async def on_command_error(self, ctx: Context, exc):
        if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
            pass
        
        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send('One or more required arguments were missed.')
            
        elif isinstance(exc.original, Forbidden):
            await ctx.send('You do not have permission to do this.')
        
        elif isinstance(exc.original, HTTPException):
            await ctx.send('Unable to send message.')
        
        else:
            raise exc.original

    async def on_ready(self):
        if not self.ready:
            self.guild = self.get_guild(823649821679681546)
            self.scheduler.add_job(self.rules_reminder, CronTrigger(
                day_of_week=0, hour=12, minute=0, second=0))
            self.scheduler.start()
            
            # channel: TextChannel = self.guild.system_channel
            # await channel.send('Bot is online!')
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
            while not self.cogs_ready.all_ready():
                await sleep(0.5)
            self.ready = True
            print('[INFO] Bot is ready.')
        else:
            print('[INFO] Bot reconnected.')

    async def on_message(self, message: Message):
        if message.author.bot:
            return
        await self.process_commands(message)


bot = Bot()
