import datetime
from typing import Any, Dict, List

import discord
from discord.ui import button, Button, View

from utils import tz_fromiso
from silksong.silksong_utils import generate_silksong_embed

from structlog import get_logger
logger = get_logger(__name__)


class NewsView(View):
    def __init__(self,
                 *args,
                 news_list: List[Dict[str, Any]],
                 news_today=False,
                 timeout: int = 300.0,
                 **kwargs):
        super().__init__(*args, timeout=timeout, **kwargs)
        self.message = None
        self.news_list = news_list
        # a bit hacky but when there's no news today, we want the next page to be the
        # most recent news (-1 to start at 0) and when there's news today, we want the
        # next page to be the next oldest news (0 to start at 1)
        self.page = 0 if news_today else -1
        self._button_status_manager()

    async def on_timeout(self):
        logger.info(
            f"Disabling the Silksong view on message {self.message.id if self.message else None}"
        )
        if self.message:
            await self.message.edit(embed=self._generate_embed(), view=None)
        self.message = None
        self.prev_page.disabled = True
        self.next_page.disabled = True

    @button(label='More recent news', style=discord.ButtonStyle.blurple, disabled=True)
    async def prev_page(self, interaction: discord.Interaction, button: Button):
        self.page = self.page - 1
        if self.page < 0:
            self.page = 0

        self._button_status_manager()

        await interaction.response.edit_message(embed=self._generate_embed(), view=self)

    @button(label='Previous news', style=discord.ButtonStyle.blurple, disabled=True)
    async def next_page(self, interaction: discord.Interaction, button: Button):
        self.page = self.page + 1
        if self.page >= len(self.news_list):
            self.page = len(self.news_list)-1

        self._button_status_manager()

        await interaction.response.edit_message(embed=self._generate_embed(), view=self)

    def _button_status_manager(self):
        self.prev_page.disabled = True if self.page <= 0 else False
        self.next_page.disabled = True if self.page >= len(self.news_list) - 1 else False

    def _generate_embed(self):
        news = self.news_list[self.page]
        date = tz_fromiso(news['date'])
        description = news['message']
        if self.page < len(self.news_list) - 1:
            description += "\n\n You can check the previous news by clicking the button below."
        return generate_silksong_embed(date, description)
