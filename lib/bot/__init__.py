from unicodedata import name
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from asyncio import sleep

from discord import Intents, TextChannel, Message
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import CommandNotFound, BadArgument, MissingRequiredArgument, CommandOnCooldown, CheckFailure
from discord.errors import HTTPException, Forbidden
from discord.ext.commands import Context, when_mentioned_or

from glob import glob

from lib.db import db

OWNER_IDS = [341671286415687692]
COGS = [path.split('\\')[-1][:-3] for path in glob('./lib/cogs/*.py')]
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)


def get_prefix(bot, message):
    sql_query = 'SELECT Prefix FROM guilds WHERE GuildID = ?'
    sql_data = message.guild.id
    prefix = db.field(sql_query, sql_data)
    return when_mentioned_or(prefix)(bot, message)


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
        self.ready = False
        self.cogs_ready = Ready()
        self.guild = None
        self.scheduler = AsyncIOScheduler()

        db.autosave(self.scheduler)

        super().__init__(
            command_prefix=get_prefix,
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
        elif isinstance(exc, CommandOnCooldown):
            await ctx.send(f'This command on cooldown. Try againt in {exc.retry_after:,.2f} secs.')
        elif hasattr(exc, 'original'):
            if isinstance(exc.original, Forbidden):
                await ctx.send('You do not have permission to do this.')
            elif isinstance(exc.original, HTTPException):
                await ctx.send('Unable to send message.')
            else:
                raise exc.original
        else:
            raise exc

    async def on_ready(self):
        self.guild = self.get_guild(823649821679681546)
        self.scheduler.add_job(self.rules_reminder, CronTrigger(
            day_of_week=0, hour=12, minute=0, second=0))
        self.scheduler.start()
        if not self.ready:
            while not self.cogs_ready.all_ready():
                await sleep(0.2)
            self.ready = True
            print('[INFO] Bot is ready.')
        else:
            print('[INFO] Bot reconnected.')

    async def on_message(self, message: Message):
        if message.author.bot:
            return
        await self.process_commands(message)


bot = Bot()
