import config
import discord
from discord.ext import commands

from structlog import get_logger
from config import BOT_PREFIX
logger = get_logger(__name__)

intents = discord.Intents().all()
# client = discord.Client(intents=intents)


class Bot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.sync = False
        self.cog_classes = []
        self.groups = []
        self.tasks = []

    async def on_ready(self):
        if config.DEV_CHANNEL_ID is None:
            return

        dev_channel = self.get_channel(config.DEV_CHANNEL_ID)
        commit_msg = ''
        if config.LAST_COMMIT_MSG:
            commit_msg = f'Commit {
                "on branch [" + config.LAST_COMMIT_BRANCH + "]" if config.LAST_COMMIT_BRANCH else ""
            }: {config.LAST_COMMIT_MSG}'
        await dev_channel.send(
            f'DIABLO Strike restarted and ready! {commit_msg}'
        )

        for task in self.tasks:
            task.start()

    async def setup_hook(self):
        logger.info(f"Will sync: {'yes' if self.sync else 'no'}")

        for cog_class in self.cog_classes:
            await self.add_cog(cog_class(self))

        for grp in self.groups:
            self.tree.add_command(grp)

        self.tree.copy_global_to(guild=discord.Object(id=908128228701536266))

        if self.sync:
            await self.tree.sync(guild=discord.Object(id=908128228701536266))


client = Bot(command_prefix=BOT_PREFIX, intents=intents)
