import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord.ext.commands.context import Context
from discord import Member, Role
import config
import datetime
import asyncio
import random
import json
from utils import find_vc
from typing import Optional, Union
from anime import (
    handle_anime,
    handle_manga,
    handle_ranime
)
from sys import platform
import structlog

logger = structlog.get_logger(__name__)

intents = discord.Intents().all()
# client = discord.Client(intents=intents)
client = commands.Bot(command_prefix='?', intents=intents)

DS_INC = False

important_stuff = {}

@client.command(aliases=['a'])
async def anime(ctx, name, *args):
    await handle_anime(ctx, name, *args)


@client.command(aliases=['m', 'ma'])
async def manga(ctx, name, *args):
    await handle_manga(ctx, name, *args)


@client.command(aliases=['ra'])
async def ranime(ctx):
    await handle_ranime(ctx)


@has_permissions(administrator=True)
@client.command(aliases=['pconf'])
async def punishconf(ctx: Context, config: str, arg: Union[Role, str]):
    with open('data/punishment_roles.json', 'r') as conf:
        current_conf = json.load(conf)

    match config.lower():
        case 'role' | 'r':
            if not isinstance(arg, Role):
                await ctx.channel.send('You should mention the role with "@"')
                return
            guild_conf = current_conf.get(str(ctx.guild.id), {})
            guild_conf['role'] = arg.id
            current_conf[str(ctx.guild.id)] = guild_conf

        case 'channel' | 'ch' | 'c':
            arg = str(arg)
            vc = find_vc(ctx.guild, arg)
            if vc is None:
                await ctx.channel.send(f'Voice channel "{arg}" not found.')
                return
            guild_conf = current_conf.get(str(ctx.guild.id), {})
            guild_conf['channel'] = vc.id
            current_conf[str(ctx.guild.id)] = guild_conf

        case _:
            await ctx.channel.send('Not a valid config.')
            return

    with open('data/punishment_roles.json', 'w') as conf:
        json.dump(current_conf, conf)

    await ctx.channel.send('OK')


@client.command(aliases=['gulag', 'g', 'p'])
async def punish(ctx: Context, user: Member):
    # get punishment role
    with open('data/punishment_roles.json', 'r') as f_punishment_roles:
        punishment_roles_dict = json.load(f_punishment_roles)

    guild_conf = punishment_roles_dict.get(str(ctx.guild.id), None)

    if not guild_conf or not guild_conf.get('role', None):
        await ctx.channel.send('It seems that this feature is not configured yet on this server\n'
                               'To do so create a role with preferred permissions and add it '
                               'to my database sending ?punishconf role @role')

    if ctx.guild.get_role(guild_conf.get('role')) in user.roles and \
            ctx.guild.owner != ctx.author:
        await ctx.channel.send('You do not have permission')
        return

    initial_roles = user.roles[1:]
    logger.info(initial_roles)
    vc_stat = user.voice
    await user.remove_roles(*initial_roles, reason='punishment')

    # save punished user initial data
    with open('data/punished_users.json', 'r') as f_pu:
        pu_dict = json.load(f_pu)

    pu_dict[str(user.id)] = {
        'initial_roles': [role.id for role in initial_roles],
        'initial_vc': vc_stat.channel.id if vc_stat and vc_stat.channel else None
    }

    with open('data/punished_users.json', 'w') as f_pu:
        json.dump(pu_dict, f_pu)

    await user.add_roles(ctx.guild.get_role(guild_conf['role']))

    if user.voice and guild_conf.get('channel', None):
        await user.move_to(ctx.guild.get_channel(guild_conf['channel']))

    await ctx.channel.send(f'User {user.mention} was punished')


# @has_permissions(move_members=True, manage_roles=True)
@client.command(aliases=['pa', 'forgive', 'f'])
async def pardon(ctx: Context, user: Member):
    with open('data/punishment_roles.json', 'r') as f_punishment_roles:
        punishment_roles_dict = json.load(f_punishment_roles)
        guild_conf = punishment_roles_dict.get(str(ctx.guild.id))
        punishment_role = guild_conf['role']

    if ctx.guild.get_role(punishment_role) in user.roles and \
            ctx.guild.owner != ctx.author:
        await ctx.channel.send('You do not have permission')
        return

    with open('data/punished_users.json', 'r') as f_pu:
        pu_dict = json.load(f_pu)

    logger.info(pu_dict)

    user_recovery_data = pu_dict.pop(str(user.id), None)
    logger.info(pu_dict)

    if not user_recovery_data:
        await ctx.channel.send('This user is not punished')
        return

    with open('data/punished_users.json', 'w') as f_pu:
        logger.info(pu_dict)
        json.dump(pu_dict, f_pu)

    await user.remove_roles(ctx.guild.get_role(punishment_role), reason='pardon')
    await user.add_roles(
        *[ctx.guild.get_role(role_id) for role_id in user_recovery_data['initial_roles']],
        reason='pardon'
    )
    if user.voice and user_recovery_data.get('initial_vc', None):
        await user.move_to(ctx.guild.get_channel(user_recovery_data['initial_vc']))

    await ctx.channel.send('OK')


@client.command()
async def activeitou(ctx):
    with open('assets/ActivateWindows.png', 'rb') as img:
        f = discord.File(img, filename='ActivateWindows.png')
        await ctx.channel.send(file=f)


@client.command(aliases=['minecraft', 'coordinates', 'coords'])
async def meinkampf(ctx):
    with open('assets/minecraft_coords.txt', 'r') as file:
        coords = file.readlines()
        coords.sort(key=lambda v: v.lower())
        string_coords = ''.join(coords)

    await ctx.channel.send(string_coords)


@client.command(aliases=['addCoords', 'newCoords', 'addCoordinates', 'newCoordinates'])
async def add_coords(ctx, coord, *args):
    for arg in args:
        coord += f' {arg}'
    coord += '\n'
    with open('assets/minecraft_coords.txt', 'a') as file:
        file.write(coord)

    await ctx.channel.send('New coordinates added')


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

async def launch_diablo_strike(message):
    move_to = find_vc(message.guild, config.DEATH_CHANNEL)
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
        logger.info(f'({message.author.id}) {message.author}: {message.content}')
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
        logger.info(important_stuff)
        await message.channel.send('OK')
        return

    await client.process_commands(message)


def main():
    client.run(config.DISCORD_BOT_TOKEN)


if __name__ == '__main__':
    main()
