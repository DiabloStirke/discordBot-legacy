import discord
from controlpanel_client import ControlPanelClient
from utils import tz_fromiso, tz_now, ordinal
from silksong.silksong_utils import generate_silksong_embed
from silksong.ui import NewsView

from structlog import get_logger
logger = get_logger(__name__)


@discord.app_commands.command(name="silksong")
async def silksong(interaction: discord.Interaction):
    """ Get the latest silksong news.
    """
    control_panel = ControlPanelClient()
    today = tz_now()
    try:
        news = control_panel.get_silksong_news()
    except Exception as e:
        logger.exception("Error fetching news", exc_info=e)
        description = ("An error occurred while fetching the news..." +
                       " Let's just say there are no news for today.")
        embed = generate_silksong_embed(today, description, False)
        await interaction.response.send_message(embed=embed)
        return

    last_news = news[0] if len(news) >= 1 else None
    last_news_date = tz_fromiso(last_news['date']) if last_news else None
    days = (today - last_news_date).days if last_news_date else "INFINITE"

    news_today = False
    if last_news and today.date() == last_news_date.date():
        description = last_news['message']
        news_today = True
    else:
        formatted_date = f"{today.strftime('%B')} {ordinal(today.day)} {today.year}"
        description = (f"Today is {formatted_date}. " +
                       "There has been no news to report for silksong for today." +
                       f"\n\nThere were no news for the past {days} days.")
        if len(news) >= 1:
            description += (" Though you can check the previous news by clicking " +
                            'the "Previous news" button below.')

    embed = generate_silksong_embed(today, description, news_today)

    if (len(news) >= 1):
        view = NewsView(news_list=news, news_today=news_today)
        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_response()
    else:
        await interaction.response.send_message(embed=embed)
