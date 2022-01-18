import discord
from discord.ext import commands
from discord.ext.commands.context import Context
import config
import asyncio
import random
from anime import (
    handle_anime,
    handle_manga,
    handle_ranime
)


intents = discord.Intents().all()
# client = discord.Client(intents=intents)
client = commands.Bot(command_prefix='?', intents=intents)

DS_INC = False

important_stuff = {}


@client.command()
async def anime(ctx, name, *args):
    await handle_anime(ctx, name, *args)


@client.command()
async def manga(ctx, name, *args):
    await handle_manga(ctx, name, *args)


@client.command()
async def ranime(ctx):
    await handle_ranime(ctx)


@client.command()
async def purei(ctx):
    print('AA', ctx)
    vc = ctx.author.voice.channel
    voice = ctx.voice_client
    if not voice:
        await vc.connect()
        voice = ctx.voice_client

    voice.play(discord.FFmpegPCMAudio(executable='ffmpeg/bin/ffmpeg.exe', source='assets/nggyu.mp3'))

@client.command()
async def fuckoff(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

@client.command()
async def a(ctx):
    await ctx.channel.send('a')


async def launch_diablo_strike(message):
    move_to = None
    for _vc in message.guild.voice_channels:
        if config.DEATH_CHANNEL == _vc.name:
            move_to = _vc
    vc = message.author.voice
    if not vc:
        await message.channel.send("To use DIABLO Strike start a run (join any voice channel)")
        return
    vc = vc.channel
    if vc.name == config.DEATH_CHANNEL:
        await message.channel.send("Can't do it, reason: omae wa mou shindeiru")
        return
    await message.channel.send("20 seconds to drop OGM-72 'DIABLO' Strike")
    await asyncio.sleep(10)
    await message.channel.send("10 seconds...")
    await asyncio.sleep(5)
    await message.channel.send('5 seconds...')
    await asyncio.sleep(5)
    await message.channel.send('DIABLO STRIKE')
    members = vc.members
    if not members:
        await message.channel.send("It seems everyone has escaped the death")
        return
    member_to_die = members[random.randint(0, len(members)-1)]
    await message.channel.send(f"The member to die is {member_to_die.mention}")
    await member_to_die.move_to(move_to)


@client.event
async def on_message(message):
    # if message.author.id == 370953016951439361: #joey
    #     await message.channel.send('Joey... está feo que robes waifus')
    #     return

    if message.author == client.user:
        return

    global DS_INC, important_stuff

    if isinstance(message.channel, discord.DMChannel) and message.author.id == 369546906449346560:
        print(f'({message.author.id}) {message.author}: {message.content}')
        # if message.author.id == 370953016951439361: #joey
        #     await message.channel.send('No lo repetiré, está feo que robes waifus')
        #     return
        if '_change_channel' in message.content.lower():
            channel_name = message.content.lower().split(' ')[1]
            important_stuff['current'] = important_stuff[f'tl_{channel_name}']
            await message.channel.send('OK')
            return
        ch = important_stuff['current']
        await ch.send(message.content)
        return

    if message.content.lower() == 'shift':
        if not DS_INC:
            DS_INC = True
            await launch_diablo_strike(message)
            DS_INC = False
        else:
            await message.channel.send(f"Your DIABLO STRIKE is on cooldown.")

    if message.content.lower() == 'moneda':
        if random.randint(0, 1):
            await message.channel.send('Cara')
        else:
            await message.channel.send('Cruz')

    if 'abogado' in message.content.lower() and message.author.id == 369546906449346560:
        await message.channel.send(f"Hola, soy el abogado del Ruso.")

    if 'dm' in message.content.lower() and message.author.id == 369546906449346560:
        dm = message.author.dm_channel()
        if not dm:
            dm = await message.author.create_dm()
        await dm.send(f'Diablo strike dm')

    if 'setup' in message.content.lower() and message.author.id == 369546906449346560:
        important_stuff['tanto_luore'] = message.guild
        for ch in message.guild.channels:
            if isinstance(ch, discord.VoiceChannel):
                continue
            important_stuff[f'tl_{ch.name}'] = ch
        important_stuff['current'] = important_stuff[f'tl_general']
        print(important_stuff)
        await message.channel.send('OK')
        return

    await client.process_commands(message)

def main():
    client.run(config.DISCORD_BOT_TOKEN)


if __name__ == '__main__':
    main()
