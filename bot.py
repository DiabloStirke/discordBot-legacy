import discord
from discord.ext import commands
from discord.ext.commands.context import Context
import config
import asyncio
import random
from selenium.webdriver.common.by import By
from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as excond
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException
import requests
from lxml import etree
from io import StringIO

firefox_options = FirefoxOptions()
firefox_options.add_argument("window-size=1920,1080")
firefox_options.add_argument('--disable-web-security')
# firefox_options.add_argument('--start-maximized')
firefox_options.add_argument('--no-sandbox')
firefox_options.add_argument('--trace-to-console')
firefox_options.add_argument('--trace-startup')
# firefox_options.add_argument('--screenshot')
firefox_options.add_argument('--headless')
firefox_options.add_argument('--disable-dev-shm-usage')
firefox_options.set_preference('intl.accept_languages', 'en-US, en')

ignored_exceptions = (StaleElementReferenceException, )


intents = discord.Intents().all()
# client = discord.Client(intents=intents)
client = commands.Bot(command_prefix='?', intents=intents)

DS_INC = False

important_stuff = {}


def get_webpage(url):
    response = requests.get(url)
    dom_tree = etree.parse(
        StringIO(response.content.decode('utf-8')),
        parser=etree.HTMLParser()
    )

    return dom_tree

@client.command()
async def anime(ctx: Context, name: str, *args):
    for arg in args:
        name += f' {arg}'
    if len(name) <= 2:
        await ctx.channel.send(f'The name must be at least 3 characters long.')
        return
    await ctx.channel.send(f'Searching in MyAnimeList for {name}...')

    mal_page = get_webpage(f'https://myanimelist.net/search/all?q={name}&cat=all')
    first_link = mal_page.xpath('//article[1]//a[1]')[0].get('href')

    mal_page = get_webpage(first_link)

    img_src = mal_page.xpath('//*[@class="borderClass"]//img[1]')[0].get('data-src')
    title = mal_page.xpath('//h1[contains(@class, "title-name")]')[0].getchildren()[0].text
    try:
        eng_title = mal_page.xpath('//p[contains(@class, "title-english")]')[0].text
    except IndexError:
        eng_title = None

    # save image
    response = requests.get(img_src)
    response.raise_for_status()

    with open('assets/AnimePic.png', 'wb') as img:
        img.write(response.content)

    # send image
    with open('assets/AnimePic.png', 'rb') as img:
        f = discord.File(img, filename='search_result.png')
        title_string = f'**{title}**' + (f' ({eng_title})' if eng_title else '')
        await ctx.channel.send(f'Result from MyAnimeList <{first_link}> \n\n'
                               f'{title_string}', file=f)

@client.command()
async def anime_slow(ctx: Context, name: str, *args):
    for arg in args:
        name += f' {arg}'
    if len(name) <= 2:
        await ctx.channel.send(f'The name must be at least 3 characters long.')
        return
    await ctx.channel.send(f'Searching in MyAnimeList for {name}...')
    browser = Firefox(options=firefox_options)
    browser.get(f'https://myanimelist.net/search/all?q={name}&cat=all')
    # sell bot's soul to devil (accept cookies)
    try:
        button = WebDriverWait(browser, 0.5, ignored_exceptions=ignored_exceptions).until(
            excond.presence_of_element_located(
                (By.XPATH, '//button[contains(text(), "AGREE")]')
            )
        )
    except TimeoutException:
        print('skipped cookie acceptation')
    else:
        button.click()

    WebDriverWait(browser, 1, ignored_exceptions=ignored_exceptions).until(
        excond.presence_of_element_located(
            (By.XPATH, f"//div[contains(text(), 'Search Results for \"{name}\"')]"))
    )
    # get the first result
    first_link = browser.find_element(By.XPATH, '//article[1]//a[1]').get_attribute('href')
    browser.get(first_link)
    img_src = WebDriverWait(browser, 1, ignored_exceptions=ignored_exceptions).until(
        excond.presence_of_element_located((By.XPATH, '//*[@class="borderClass"]//img[1]'))
    ).get_attribute('src')
    title = browser.find_element(By.XPATH, '//h1[contains(@class, "title-name")]').text
    try:
        eng_title = browser.find_element(By.XPATH, '//p[contains(@class, "title-english")]').text
    except NoSuchElementException:
        eng_title = None
    browser.close()

    # save image
    response = requests.get(img_src)
    response.raise_for_status()
    with open('assets/AnimePic.png', 'wb') as img:
        img.write(response.content)

    # send image
    with open('assets/AnimePic.png', 'rb') as img:
        f = discord.File(img, filename='search_result.png')
        title_string = f'**{title}**' + (f' ({eng_title})' if eng_title else '')
        await ctx.channel.send(f'Result from MyAnimeList <{first_link}> \n\n'
                               f'{title_string}', file=f)








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

    if isinstance(message.channel, discord.DMChannel):
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
