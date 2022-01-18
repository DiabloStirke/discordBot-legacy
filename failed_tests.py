from bot import client
import discord
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as excond
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException
from discord.ext.commands.context import Context

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
