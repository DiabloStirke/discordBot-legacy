from utils import get_webpage
import config
import discord
import requests
import random
from discord.ext.commands.context import Context


async def send_anime_info(url, ctx):
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

    with open('assets/AnimePic.png', 'wb') as img:
        img.write(response.content)

    # send image
    with open('assets/AnimePic.png', 'rb') as img:
        f = discord.File(img, filename='search_result.png')
        title_string = f'**{title}**' + (f' ({eng_title})' if eng_title else '')
        score_string = '\n**Score:** ' + (f'{score}/10' if score != 'N/A' else '*not rated*')
        if not score:
            score_string = ''
        await ctx.channel.send(f'Result from MyAnimeList <{url}> \n\n'
                               f'{title_string}{score_string}', file=f)


async def handle_ranime(ctx: Context):
    num_pages = config.MAL_MAX_ANIMES//config.MAL_ANIMES_PER_PAGE
    page = random.randint(0, num_pages)
    num_animes = config.MAL_ANIMES_PER_PAGE
    if page == num_pages:
        num_animes = config.MAL_MAX_ANIMES % config.MAL_ANIMES_PER_PAGE or 50
    anime = random.randint(1, num_animes)
    print(f'https://myanimelist.net/topanime.php?limit={page*50}, anime {anime}')

    all_animes = get_webpage(f'https://myanimelist.net/topanime.php?limit={page*50}')
    rnd_link = all_animes.xpath(
        f'//table[contains(@class, "top-ranking")]//tr[@class="ranking-list"][{anime}]//a[1]'
    )[0].get('href')

    await send_anime_info(rnd_link, ctx)


async def handle_anime(ctx: Context, name: str, *args):
    for arg in args:
        name += f' {arg}'
    if len(name) <= 2:
        await ctx.channel.send(f'The name must be at least 3 characters long.')
        return
    await ctx.channel.send(f'Searching in MyAnimeList for {name}...')

    mal_page = get_webpage(f'https://myanimelist.net/anime.php?q={name}&cat=anime')
    first_link = mal_page.xpath('//table/tr[2]//div[@class="title"]//a[1]')[0].get('href')

    await send_anime_info(first_link, ctx)


async def handle_manga(ctx: Context, name: str, *args):
    for arg in args:
        name += f' {arg}'
    if len(name) <= 2:
        await ctx.channel.send(f'The name must be at least 3 characters long.')
        return
    await ctx.channel.send(f'Searching in MyAnimeList for {name}...')

    mal_page = get_webpage(f'https://myanimelist.net/manga.php?q={name}&cat=manga{name}')
    first_link = mal_page.xpath('//table/tr[2]//a[1]')[0].get('href')

    await send_anime_info(first_link, ctx)
