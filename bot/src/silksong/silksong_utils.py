import datetime
import discord
import config
from utils import ordinal


def message_prepend(d: datetime.datetime) -> str:
    date = d.date()
    today = datetime.datetime.now(tz=config.TZINFO).date()
    formatted_date = f"{date.strftime('%B')} {ordinal(date.day)} {date.year}"
    if date == today:
        return f"Today is {formatted_date}. There are silksong news today!"
    elif date == today - datetime.timedelta(days=1):
        return f"Yesterday was {formatted_date}. There were silksong news yesterday!"
    else:
        return f"There were silksong news on {formatted_date}!"


def generate_silksong_embed(date: datetime.datetime, description, prepend=True) -> discord.Embed:
    if prepend:
        description = f"{message_prepend(date)} {description}"

    embed = discord.Embed(
        title="Daily Silksong News",
        url="https://www.youtube.com/@DailySilksongNews",
        color=13587467,
        description=description
    )
    embed.set_thumbnail(
        url="https://sm.ign.com/t/ign_nordic/cover/h/hollow-kni/hollow-knight-silksong_46ud.128.jpg"
    )
    return embed
