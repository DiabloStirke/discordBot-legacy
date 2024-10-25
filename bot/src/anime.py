from utils import get_webpage
import config
import discord
import requests
import random
import asyncio
from discord.ext.commands.context import Context
import structlog
from bot_config import client

logger = structlog.get_logger(__name__)


async def send_anime_info(url, ctx, wish=False):
    mal_page = get_webpage(url)

    img_src = mal_page.xpath('//*[@class="borderClass"]//img[1]')[0].get('data-src')
    try:
        title = mal_page.xpath('//h1[contains(@class, "title-name")]')[0].getchildren()[0].text
    except IndexError:
        title = mal_page.xpath('//span[@itemprop="name"]')[0].text
    try:
        eng_title = mal_page.xpath('//*[contains(@class, "title-english")]')[0].text
    except IndexError:
        eng_title = None
    try:
        score = mal_page.xpath('//div[contains(@class, "score-label")]')[0].text
    except IndexError:
        score = None
    # save image
    response = requests.get(img_src)
    response.raise_for_status()

    with open('../assets/AnimePic.png', 'wb') as img:
        img.write(response.content)

    if wish:
        wish_file = None
        try:
            score_int = float(score)
        except ValueError:
            score_int = 0.0
        if score_int >= 8:
            wish_file = '../assets/genshin_wish_5star.gif'
        elif score_int >= 6.66:
            wish_file = '../assets/genshin_wish_4star.gif'
        if wish_file:
            with open(wish_file, 'rb') as gif:
                f = discord.File(gif, filename='wish.gif')
                await ctx.channel.send(file=f)
                await asyncio.sleep(6)

    # send image
    with open('../assets/AnimePic.png', 'rb') as img:
        f = discord.File(img, filename='search_result.png')
        title_string = f'**{title}**' + (f' ({eng_title})' if eng_title else '')
        score_string = '\n**Score:** ' + (f'{score}/10' if score != 'N/A' else '*not rated*')
        if not score:
            score_string = ''
        await ctx.channel.send(f'Result from MyAnimeList <{url}> \n\n'
                               f'{title_string}{score_string}', file=f)


@client.command(aliases=['ra'])
async def ranime(ctx: Context):
    num_pages = config.MAL_MAX_ANIMES//config.MAL_ANIMES_PER_PAGE
    page = random.randint(0, num_pages)
    num_animes = config.MAL_ANIMES_PER_PAGE
    if page == num_pages:
        num_animes = config.MAL_MAX_ANIMES % config.MAL_ANIMES_PER_PAGE or 50
    anime = random.randint(1, num_animes)
    logger.info(f'https://myanimelist.net/topanime.php?limit={page*50}, anime {anime}')

    all_animes = get_webpage(f'https://myanimelist.net/topanime.php?limit={page*50}')
    rnd_link = all_animes.xpath(
        f'//table[contains(@class, "top-ranking")]//tr[@class="ranking-list"][{anime}]//a[1]'
    )[0].get('href')

    await send_anime_info(rnd_link, ctx, wish=True)


@client.command(aliases=['a'])
async def anime(ctx: Context, name: str, *args):
    for arg in args:
        name += f' {arg}'
    if len(name) <= 2:
        await ctx.channel.send(f'The name must be at least 3 characters long.')
        return
    await ctx.channel.send(f'Searching in MyAnimeList for {name}...')

    mal_page = get_webpage(f'https://myanimelist.net/anime.php?q={name}&cat=anime')
    first_link = mal_page.xpath('//table/tr[2]//div[@class="title"]//a[1]')[0].get('href')

    await send_anime_info(first_link, ctx)


@client.command(aliases=['m', 'ma'])
async def manga(ctx: Context, name: str, *args):
    for arg in args:
        name += f' {arg}'
    if len(name) <= 2:
        await ctx.channel.send(f'The name must be at least 3 characters long.')
        return
    await ctx.channel.send(f'Searching in MyAnimeList for {name}...')

    mal_page = get_webpage(f'https://myanimelist.net/manga.php?q={name}&cat=manga{name}')
    first_link = mal_page.xpath('//table/tr[2]//a[1]')[0].get('href')

    await send_anime_info(first_link, ctx)
