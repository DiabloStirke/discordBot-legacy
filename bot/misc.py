import discord

from bot_config import client
from utils import find_vc, ordinal
import config
import asyncio
import datetime
import random
from structlog import get_logger
from special_rules import check_choose_cheat

logger = get_logger(__name__)

important_stuff = {}
DS_INC = {}


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


@client.command(aliases=['shift', 'diablo_strike', 'DIABURO_STORAIKU'])
async def launch_diablo_strike(ctx):
    global DS_INC

    if not DS_INC.get(str(ctx.guild.id), False):
        DS_INC[str(ctx.guild.id)] = True
    else:
        await ctx.channel.send(f"Your DIABLO STRIKE is on cooldown.")
        return

    move_to = find_vc(ctx.guild, config.DEATH_CHANNEL)
    vc = ctx.author.voice
    if not vc:
        await ctx.channel.send("To use DIABLO Strike start a run (join any voice channel)")
        DS_INC.pop(str(ctx.guild.id), None)
        return
    vc = vc.channel
    if vc.name == config.DEATH_CHANNEL:
        await ctx.channel.send("Can't do it, reason: omae wa mou shindeiru")
        DS_INC.pop(str(ctx.guild.id), None)
        return
    await ctx.channel.send("20 seconds to drop OGM-72 'DIABLO' Strike")
    await asyncio.sleep(10)
    await ctx.channel.send("10 seconds...")
    await asyncio.sleep(5)
    await ctx.channel.send('5 seconds...')
    await asyncio.sleep(5)
    await ctx.channel.send('DIABLO STRIKE')
    members = vc.members
    if not members:
        await ctx.channel.send("It seems everyone has escaped the death")
        DS_INC.pop(str(ctx.guild.id), None)
        return
    member_to_die = members[random.randint(0, len(members)-1)]
    await ctx.channel.send(f"The member to die is {member_to_die.mention}")
    await member_to_die.move_to(move_to)
    DS_INC.pop(str(ctx.guild.id), None)


@client.command()
async def moneda(ctx):
    if random.randint(0, 1):
        await ctx.channel.send('Cara')
    else:
        await ctx.channel.send('Cruz')


@client.command(aliases=['pick', 'select', 'choice'])
async def choose(ctx, *args):
    if len(args) == 0:
        await ctx.channel.send("I mean... given this wide list of options, I guess I'll choose nothing.")
        return

    arg_str = " ".join(args)

    num_ls = arg_str.replace(" ", "").split('-')
    if len(num_ls) == 2:
        try:
            num1 = int(num_ls[0])
            num2 = int(num_ls[1])
            if num2 < num1:
                raise ValueError("First operand is greater than the second")
        except ValueError:
            pass
        else:
            await ctx.channel.send(random.randint(num1, num2))
            return

    str_list = arg_str.split(',') if ',' in arg_str else args
    
    str_list = list(filter(lambda x: bool(x.strip()), str_list))
    
    if len(str_list) == 0:
        await ctx.channel.send("I mean... given this wide list of options, I guess I'll choose nothing.")

    # found_cheat, result = check_choose_cheat(str_list, ctx.author.id)
    #
    # if found_cheat:
    #     await ctx.channel.send(result)

    # else:
    await ctx.channel.send(random.choice(str_list))


@client.command(aliases=['purge', 'clear'])
async def clean(ctx, limit=1):
    if limit > 100:
        await ctx.channel.send("Woah, calm down a bit. That's too much, don't you think?")
        return

    await ctx.channel.purge(limit=limit+1, bulk=True)

@client.command()
async def silksong(ctx):
    last_news = datetime.datetime(year=2023, month=2, day=2)
    today = datetime.date.today()
    days = (today - last_news).days
    embed = discord.Embed(
        title="Daily Silksong News",
        url="https://www.youtube.com/@DailySilksongNews",
        color=13587467,
        description=f"Today is {today.strftime('%B')}{ordinal(today.day)} {today.year}"
                    +"There has been no news to report for silksong today\n\nThere were no news for the past {days}",
    )
    embed.set_thumbnail(
        url="https://sm.ign.com/t/ign_nordic/cover/h/hollow-kni/hollow-knight-silksong_46ud.128.jpg"
    )
    await ctx.channel.send(embed=embed)

@client.event
async def on_message(message):
    # if message.author.id == 370953016951439361: #joey
    #     await message.channel.send('Joey... está feo que robes waifus')
    #     return

    if message.author == client.user:
        return

    global important_stuff

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

    combos_str = ['zura', 'lolicon']
    combos = {combo: {'combo': list(combo)} for combo in combos_str}

    for c in message.content.lower():
        for combo in combos.values():
            if not combo.get('exists', False) and combo['combo'][0] == c:
                combo['combo'].pop(0)
                if len(combo['combo']) == 0:
                   combo['exists'] = True

    if combos['zura'].get('exists', False):
        zura_gifs = [
            'https://tenor.com/view/gintama-punch-gif-9531089',
            'https://tenor.com/view/anime-gintama-pat-punch-gif-7885609',
            'https://tenor.com/view/gintama-katsura-zura-its-not-afro-its-katsura-gif-15425161',
            'https://tenor.com/view/gintama-zura-anime-gif-9531133'
        ]
        await message.channel.send("Zura janai, Katsura da!")
        await message.channel.send(random.choice(zura_gifs))

    if combos['lolicon'].get('exists', False):
        loli_gifs = [
            'https://tenor.com/view/lolicon-feminist-gintama-meme-anime-gif-17004204'
        ]
        await message.channel.send('Lolicon janai, femenisto desu!')
        await message.channel.send(random.choice(loli_gifs))


    #  TODO Decide whether to delete or move somewhere else
    # if 'abogado' in message.content.lower() and message.author.id == 369546906449346560:
    #     await message.channel.send(f"Hola, soy el abogado del Ruso.")
    #
    # if 'dm' in message.content.lower() and message.author.id == 369546906449346560:
    #     dm = message.author.dm_channel()
    #     if not dm:
    #         dm = await message.author.create_dm()
    #     await dm.send(f'Diablo strike dm')
    #
    # if 'setup' in message.content.lower() and message.author.id == 369546906449346560:
    #     important_stuff['tanto_luore'] = message.guild
    #     for ch in message.guild.channels:
    #         if isinstance(ch, discord.VoiceChannel):
    #             continue
    #         important_stuff[f'tl_{ch.name}'] = ch
    #     important_stuff['current'] = important_stuff[f'tl_general']
    #     logger.info(important_stuff)
    #     await message.channel.send('OK')
    #     return

    await client.process_commands(message)
