import math
from typing import List, Dict, Any

import discord
from discord.ui import button, Button, View

from structlog import get_logger

logger = get_logger(__name__)

class ViewsManager:
    def __init__(self):
        self.queue_view = QueueView(queue=None, timeout=1)


class QueueView(View):    
    def __init__(self, *args, queue: List[Dict[str, Any]], timeout: int = 300.0, **kwargs):
        super().__init__(*args, timeout=timeout, **kwargs)
        
        self.message: discord.InteractionMessage = None
        self.page: int = 0
        self.page_size: int = 10
        self.embeds: List[discord.Embed] = self._generate_embeds(queue)
        
        self.disabled = True
    
    
    async def first_message(self, interaction:discord.Interaction):
        self.disabled = False
        self.page = 0
        self._button_status_manager()
        await interaction.response.send_message(embed=self.embeds[0], view=self)
        self.message = await interaction.original_response()


    async def on_queue_update(self, queue: List[Dict[str, Any]]):
        if self.disabled:
            return
        
        logger.info(f"Updated the queue of the view on message {self.message.id if self.message else None}")

        self.embeds = self._generate_embeds(queue=queue)

        if self.page >= self.num_pages:
            self.page = self.num_pages - 1
        
        self._button_status_manager()

        await self.message.edit(embed=self.embeds[self.page], view=self)

    async def on_timeout(self):
        logger.info(f"Disabling the view on message {self.message.id if self.message else None}")
        if self.message:
            await self.message.edit(embed=self.embeds[self.page], view=None)
        self.message = None
        self.disabled = True
        self.prev_page.disabled = True
        self.next_page.disabled = True

    async def new_view(self, *args, interaction: discord.Interaction, queue: List[Dict[str, Any]], timeout: int = 300.0, **kwargs):
        await self.on_timeout()
        new_view = self.__class__(*args, queue=queue, timeout=timeout, **kwargs)
        await new_view.first_message(interaction)
        return new_view

    @button(label='Previous page', style=discord.ButtonStyle.blurple, disabled=True)
    async def prev_page(self, interaction: discord.Interaction, button: Button):
        self.page = self.page - 1
        if self.page < 0:
            self.page = 0

        self._button_status_manager()

        await interaction.response.edit_message(embed=self.embeds[self.page], view=self)


    @button(label='Next page', style=discord.ButtonStyle.blurple, disabled=True)
    async def next_page(self, interaction: discord.Interaction, button: Button):
        self.page = self.page + 1
        if self.page >= self.num_pages:
            self.page = self.num_pages-1

        self._button_status_manager()

        await interaction.response.edit_message(embed=self.embeds[self.page], view=self)
    

    def _button_status_manager(self):
        self.prev_page.disabled = True if self.page <= 0 else False
        self.next_page.disabled = True if self.page >= len(self.embeds) - 1 else False

    def _generate_embeds(self, queue: List[Dict[str, Any]]) -> List[discord.Embed]:
        self.num_pages: int = math.ceil(len(queue)/self.page_size) if queue else 0
        embeds = []
        for pg in range(self.num_pages):
            embed = discord.Embed(
                title=f"Current Playlist [Page {pg+1}/{self.num_pages}]",
                url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                color=14551332,
                description="You can skip to any song with the /skip command adding to it the number of the song. \n\nExample: /skip 3\n\n"
            )
            for i, song in enumerate(queue[pg*self.page_size:(pg+1)*self.page_size]):
                embed.add_field(
                    name=f'{i+1+pg*self.page_size}.',
                    value=f'[{song["title"]}]({song["web_url"]}) - [{song["channel"]}]\nDuration: {song["duration"]}',
                    inline=False
                )
            embeds.append(embed)
        
        if len(embeds) == 0:
            self.num_pages = 1
            embed = discord.Embed(
                title=f"The playlist is empty",
                color=14551332,
                description="You can't skip to any song with the /skip command because, well, the playlist is empty.\n\n" +
                            "But you can check out this video: <https://www.youtube.com/watch?v=dQw4w9WgXcQ>"
            )
            embeds.append(embed)

        return embeds