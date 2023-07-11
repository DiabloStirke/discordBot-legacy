import config
import discord
from discord.ext import commands
from discord import app_commands

from structlog import get_logger

logger = get_logger(__name__)

intents = discord.Intents().all()
# client = discord.Client(intents=intents)


class Bot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.sync = False
        self.cog_classes = []
        self.groups = []
    
    async def on_ready(self):
        if config.DEV_CHANNEL_ID is None:
            return
        
        dev_channel = self.get_channel(config.DEV_CHANNEL_ID)
        await dev_channel.send(
            f"DIABLO Strike restarted and ready! {f'Commit : {config.LAST_COMMIT_MSG}' if config.LAST_COMMIT_MSG else ''}"
        )
        
    async def setup_hook(self):
        logger.info(f"Will sync: {'yes' if self.sync else 'no'}")
        
        for cog_class in self.cog_classes:
            await self.add_cog(cog_class(self))
        
        for grp in self.groups:
            self.tree.add_command(grp)

        self.tree.copy_global_to(guild = discord.Object(id=908128228701536266))

        if self.sync:
            await self.tree.sync(guild = discord.Object(id=908128228701536266))

client = Bot(command_prefix='?', intents=intents)
