from sys import platform
import discord
from bot_config import client


@client.command()
async def purei(ctx):

    exe_path = None
    if platform == "linux" or platform == "linux2":
        exe_path = "/usr/bin/ffmpeg"
    elif platform == "win32" or platform == "win64":
        exe_path = 'ffmpeg/bin/ffmpeg.exe'

    if not exe_path:
        ctx.channel.send("Something went wrong, I am unable to reproduce audio")
        return

    vc = ctx.author.voice.channel
    voice = ctx.voice_client
    if not voice:
        await vc.connect()
        voice = ctx.voice_client

    voice.play(discord.FFmpegPCMAudio(executable=exe_path, source='assets/nggyu.mp3'))


@client.command()
async def fuckoff(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()