import asyncio
import math
import random
from sys import platform
from time import sleep
from urllib.parse import urlparse, parse_qs

import discord
from bot_config import client
from discord import app_commands
from discord.ext import commands
from utils import verbouse_time_from_seconds, valid_youtube_url
from yt_dlp import YoutubeDL
from youtube_search import YoutubeSearch

import music.ui as mui

class Music(commands.Cog):

    SONGS_PER_QUERY = 40

    def __init__(self, bot):
        self.bot = bot
        
        self.music_queue = []
        self.confirmation_list = None
        self.music_queue_size = 100
        self.songs_per_queue_page = 10
        self.views = mui.ViewsManager()

        self.FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
            'options': '-vn'
        }

        self.vc = None # voice channel 
        self.ac = None # announcement channel (Now playing message)


    @app_commands.command(name='play')
    @app_commands.rename(youtube_url='youtube_video')
    async def play(self, interaction: discord.Interaction, youtube_url: str):
        """Play a song from youtube. 
        
        Parameters
        -----------
        youtube_url: str
            A link to the youtube video. You can input any query for search results to show up as suggetions.
        """

        if not await self.check_author_vc(interaction):
            return

        if youtube_url == 'resume' and self.vc is not None and self.vc.is_paused():
            self.vc.resume()
            await interaction.response.send_message('Resuming the music player')
            return
        
        if len(self.music_queue) >= self.music_queue_size:
            await interaction.response.send_message(f"The current music queue is at is's maximum ({self.music_queue_size} songs)", ephemeral=True)
            return

        if not valid_youtube_url(youtube_url)[0]:
            await interaction.response.send_message('Invalid youtube url', ephemeral=True)
            return

        await interaction.response.defer(ephemeral=False)

        songs = self.search_yt_dl(youtube_url)

        if not songs:
            await interaction.followup.send("No such video exists", ephemeral=True)
            return
        
        song = songs[0]

        self.music_queue.append(song)

        embed = discord.Embed(title=None, description=f"Added [{song['title']}]({song['web_url']}) to the queue!", color=1675392)
        await interaction.followup.send(embed=embed)

        await self.play_music(interaction)

        await self.views.queue_view.on_queue_update(self.music_queue)
        

    @play.autocomplete('youtube_url')
    async def _songs_query(self, interaction: discord.Interaction, current):
        choices = []
        if self.paused():
            choices.append(
                app_commands.Choice(name='Resume the music player', value='resume')
            )
            
        if not current:
            return choices

        search = YoutubeSearch(current, max_results=5).to_dict()
        
        for video in search:
            choices.append(app_commands.Choice(name=video['title'], value='https://www.youtube.com/watch?v='+video['id']))

        return choices

    @app_commands.command(name='playlist')
    @app_commands.rename(youtube_url='youtube_playlist')
    async def playlist(
        self, 
        interaction: discord.Interaction, 
        youtube_url: str, 
        first_video: app_commands.Range[int, 1] = None,
        last_video: app_commands.Range[int, 1] = None,
        num_videos: app_commands.Range[int, 1, SONGS_PER_QUERY] = SONGS_PER_QUERY 
        ):
        """Play an entire playlist from youtube. Downloading of the playlist info may take a while.
        
        Parameters
        -----------
        youtube_url: str
            A link to a youtube playlist.
        first_video: int
            The first video from the playlist to be added to the song queue. If none, it will start from the selected video in the url or the first one if not specified
        last_video: int
            The last video to add to the song queue. If none it will take as much videos (starting from the first one) as specified by the num_videos parameter
        num_videos: int
            The number of videos to add to the queue. This parameter will be ignored if you specify the last video to add to the queue.
        """

        if not await self.check_author_vc(interaction):
            return

        if not valid_youtube_url(youtube_url)[1]:
            await interaction.response.send_message('Invalid youtube playlist', ephemeral=True)
            return

        if not first_video:
            url = urlparse(youtube_url)
            query = parse_qs(url.query)
            first_video = int(query['index'][0]) if query.get('index', None) is not None else 1
        
        
        if not last_video:
            last_video = first_video + num_videos - 1

        if first_video > last_video:
            await interaction.response.send_message('last_video can not be below the first_video', ephemeral=True)
            return
        
        real_num_songs = last_video - first_video + 1

        songs_over_query_limit = real_num_songs - self.SONGS_PER_QUERY

        if songs_over_query_limit > 0:
            songs = 'songs' if songs_over_query_limit > 1 else 'song' 
            await interaction.response.send_message(
                    f"Unfortunally I can only add {self.SONGS_PER_QUERY} songs in one go. You got {songs_over_query_limit} {songs} over the limit!", 
                    ephemeral=True
                )
            return

        songs_out = (real_num_songs + len(self.music_queue)) - self.music_queue_size 

        if songs_out > 0:
            songs = 'songs' if songs_out > 1 else 'song' 
            await interaction.response.send_message(f'This amount of songs will exceed the songs queue maximum capacity ({self.music_queue_size} songs) by {songs_out} {songs}.', ephemeral=True)
            return

        await interaction.response.defer(ephemeral=False)

        songs = self.search_yt_dl(youtube_url, playlist=True, start=first_video, end=last_video)

        if not songs: # "not song" is also true for empty list ({})
            await  interaction.followup.send("No such playlist exists")
            return

        for song in songs:
            self.music_queue.append(song)
        
        embed = self._generate_embed(songs)
        await interaction.followup.send(embed=embed)

        await self.play_music(interaction)

        await self.views.queue_view.on_queue_update(self.music_queue)

    @app_commands.command(name='skip')
    async def skip(self, interaction: discord.Interaction, to: app_commands.Range[int, 1] = 1):
        """Skips the current playing song to another one in the queue

        Parameters
        -----------
        to: int
            Position of the song to skip to. Defaults to the first one
        """
        if not self.connected():
            await interaction.response.send_message("I'm not connected to any VC", ephemeral=True)
            return
        
        if not self.playing() and not self.paused():
            await interaction.response.send_message("I'm not playing anything right now", ephemeral=True)
            return

        self.music_queue = self.music_queue[to-1:]

        self.vc.stop()

        await interaction.response.send_message("Skipped")

        # using /skip ALWAYS implies a call to self.next_song which already updates the queue
        # await self.views.queue_view.on_queue_update(self.music_queue) 

    @skip.autocomplete('to')
    async def _songs_query(self, interaction: discord.Interaction, current: int):
        valid_number = True
        try:
            current = int(current)
        except ValueError:
            valid_number = False

        if valid_number and current >= 1 and current <= len(self.music_queue):
            video = self.music_queue[current-1]
            return [
                app_commands.Choice(name=video['title'], value=current)
            ]
        return [
            app_commands.Choice(name=video['title'], value=idx+1)
            for idx, video in enumerate(self.music_queue[:10])
        ]

    @app_commands.command(name='queue')
    async def queue(self, interaction: discord.Interaction):
        """Lists all music that is currently in the playlist
        """
        # I defenetly wasn't planning to move the whole queue logic to the QueueView class but here we are... 
        # Although the idea of having the view based commands detached from the rest of the logic isn't that bad in my opinion...
        self.views.queue_view = await self.views.queue_view.new_view(interaction=interaction, queue=self.music_queue)
        


    @app_commands.command(name='pause')
    async def pause(self, interaction:discord.Interaction):
        """Pauses the music player
        
        """
        if not self.connected():
            await interaction.response.send_message("I'm not connected to any VC", ephemeral=True)
            return
        if not self.playing() and not self.paused():
            await interaction.response.send_message("I'm not playing anything right now", ephemeral=True)
            return
        if self.paused():
            await interaction.response.send_message("Already pasused", ephemeral=True)
            return

        self.vc.pause()

        await interaction.response.send_message("Player paused")
    
    @app_commands.command(name='disconnect')
    async def disconnect(self, interaction: discord.Interaction):
        """ Disconnect from the voice channel
        """
        if self.vc:
            await self.vc.disconnect()
            self.vc = None
            self.music_queue = []
            self.confirmation_list = None
            await interaction.response.send_message("Disconnected")
            return
        
        await interaction.response.send_message("I am not connected to any vc", ephemeral=True)
        
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if self.vc is None or self.vc.channel is None:
            return
        if len(self.vc.channel.members) > 1:
            return
        
        await self.vc.disconnect()
        self.vc = None
        self.music_queue = []
        self.confirmation_list = None

# File system sound commands 
    @app_commands.command(name='purei')
    async def purei(self, interaction):
        """ You have to find out all by yourself what this does...
        """
        await interaction.response.send_message("Never Gonna Give You Up", silent=True, ephemeral=True, delete_after=0)
        await self.play_fs_song(interaction, 'assets/nggyu.mp3')

    @app_commands.command(name='katsurap')
    async def katsurap(self, interaction):
        """ Rap janai, katsurap da yo
        """
        await interaction.response.send_message("joui ga joy", silent=True, ephemeral=True, delete_after=0)
        await self.play_fs_song(interaction, 'assets/katsurap.mp3')

# File system sound commands with a twist:
#   - play as usual if connected to a vc
#   - enter vc if not, play the song and leave vc

    @app_commands.command(name='togetha')
    async def togetha(self, interaction: discord.Interaction):
        """ Togethaa we will devour the very gods
        """
        await interaction.response.send_message("Togethaa we will devour the very gods", silent=True, ephemeral=True, delete_after=0)
        await self.play_fs_song_and_disc(interaction, f'assets/togetha{random.randint(1,2)}.mp3')

    @app_commands.command(name='shinda')
    async def shinda(self, interaction: discord.Interaction):
        """ SHINDAAAA
        """
        await interaction.response.send_message("SHINDAAA", silent=True, ephemeral=True, delete_after=0)
        await self.play_fs_song_and_disc(interaction, f'assets/shinda.mp3')

    @app_commands.command(name='malenia')
    async def malenia(self, interaction: discord.Interaction):
        """ I am Malenia, blade of Miquella
        """
        await interaction.response.send_message("Malenia... so hard...", silent=True, ephemeral=True, delete_after=0)
        await self.play_fs_song_and_disc(interaction, f'assets/malenia{random.randint(1,2)}.mp3')
    
    @app_commands.command(name='atomic')
    async def atomic(self, interaction: discord.Interaction):
        """ I... AM... *whispers* atomic
        """
        await interaction.response.send_message("I AM ATOMIC", silent=True, ephemeral=True, delete_after=0)
        await self.play_fs_song_and_disc(interaction, 'assets/atomic.mp3')

# Music player helpers

    async def play_music(self, interaction:discord.Interaction, after=None):
        if self.playing() or self.paused():
            return 

        if not self.connected():
            self.vc = await interaction.user.voice.channel.connect()
            
        song = self.music_queue.pop(0)
        
        if after is None:
            after = lambda e: asyncio.run_coroutine_threadsafe(self.next_song(), self.bot.loop)

        self.vc.play(self._generate_audiosource(song['source'], song['is_fs']), after=after)

 
    async def next_song(self):
        if not self.connected():
            self.music_queue = []

        if len(self.music_queue) > 0:
            song = self.music_queue.pop(0)
            after = lambda e: asyncio.run_coroutine_threadsafe(self.next_song(), self.bot.loop)
            self.vc.play(self._generate_audiosource(song['source'], song['is_fs']), after=after)

        await self.views.queue_view.on_queue_update(self.music_queue)
        


# File system song helpers
    async def play_fs_song(self, interaction: discord.Interaction, path):
        if not await self.check_author_vc(interaction):
            return
        self.push_fs_song(path)
        if self.playing() or self.paused():
            self.vc.stop()
            return
        
        await self.play_music(interaction)

    
    async def play_fs_song_and_disc(self, interaction: discord.Interaction, path):
        if not await self.check_author_vc(interaction):
            return
        
        self.push_fs_song(path)
        if self.playing() or self.paused():
            self.vc.stop()
            return

        after = None
        if not self.connected():
            async def wait_and_disc():
                sleep(0.75)
                await self.vc.disconnect()
            after = lambda e: asyncio.run_coroutine_threadsafe(wait_and_disc(), self.bot.loop)

        await self.play_music(interaction, after)

    def push_fs_song(self, path, title="", web_url="", channel="", duration=""):
        song = {
            'title': title, 
            'web_url': web_url,
            'channel': channel,
            'duration': duration,
            'source': path,
            'is_fs': True
        }
        self.music_queue.insert(0, song)

# Validators 
    async def check_author_vc(self, interaction: discord.Interaction):
        author_voice = interaction.user.voice
        if author_voice is None:
            await interaction.response.send_message("What's the point in playing music if you are not in any voice channel?", ephemeral=True)
            return False
        elif self.connected() and self.vc.channel.id != author_voice.channel.id:
            await interaction.response.send_message("Won't do it. It seems like we are not on the same channel.")
            return False
        return True
    
# Bot voice channel status helpers
    def connected(self):
        return self.vc is not None and self.vc.is_connected()

    def playing(self):
        return self.vc is not None and self.vc.is_playing()
    
    def paused(self):
        return self.vc is not None and self.vc.is_paused()

# Other helpers

    def search_yt_dl(self, query: str, playlist=False, start=1, end=1):

        YDL_OPTIONS = {
            'format': 'bestaudio/best',
            'restrictfilenames': True,
            'noplaylist': not playlist,
            'playliststart': start,
            'playlistend': end
        }

        if not query.startswith('https://') and not query.startswith('http://'):
            query = 'https://' + query
        with YoutubeDL(YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(query, download=False)
            except Exception:
                return False

        entries = info.get('entries', [info])
        audio_formats = {f['format']: f['url'] for f in info['formats'] if "audio only (medium)" in f['format']}

        return [{
            'title': entry['title'], 
            'web_url': entry['webpage_url'],
            'channel': entry['channel'],
            'duration': verbouse_time_from_seconds(entry['duration']),
            'source': audio_formats[list(audio_formats.keys())[0]],
            "is_fs": False
            } for entry in entries]

    @staticmethod
    def _generate_embed(search_results):
        embed = discord.Embed(
            title="YouTube Playlist",
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            color=0,
            description="Songs from this playlist were added."
        )
        for i, song in enumerate(search_results[:10]):
            embed.add_field(
                name=f'{i+1}: {song["title"]} - [{song["channel"]}]',
                value=f'Duration: {song["duration"]}\nURL: {song["web_url"]}',
                inline=False
            )

        extras = len(search_results) - 10

        if extras > 0:
            embed.add_field(
                name=f'+{extras} other song{"s" if extras > 1 else ""}',
                value='Use /queue to see them all',
                inline=False
            )
        return embed

    def _generate_audiosource(self, url, is_fs=False):
        exe_path = None
        if platform == "linux" or platform == "linux2":
            exe_path = "/usr/bin/ffmpeg"
        elif platform == "win32" or platform == "win64":
            exe_path = '../ffmpeg/bin/ffmpeg.exe'
        
        if is_fs:
            return discord.FFmpegPCMAudio(url, executable=exe_path)

        return discord.FFmpegPCMAudio(url, executable=exe_path, **self.FFMPEG_OPTIONS)