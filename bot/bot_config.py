import discord
from discord.ext import commands

intents = discord.Intents().all()
# client = discord.Client(intents=intents)
client = commands.Bot(command_prefix='?', intents=intents)

