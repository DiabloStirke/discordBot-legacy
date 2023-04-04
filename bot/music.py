from sys import platform
import discord
from discord.ext import commands
from bot_config import client
from youtube_dl import YoutubeDL 
from utils import valid_url, verbouse_time_from_seconds

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self.music_queue = []
        self.confirmation_list = None

        self.YDL_OPTIONS = {
            'format': 'bestaudio/best',
            'restrictfilenames': True,
            'noplaylist': True
        }
        self.FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
            'options': '-vn'
        }

        self.vc = None

    def search_yt(self, query):
        if not valid_url(query):
            query = f"ytsearch5:{query}"

        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try: 
                info = ydl.extract_info(query, download=False)
            except Exception: 
                return False
            
        entries = info.get('entries', [info])

        return [{
            'title': entry['title'], 
            'web_url': entry['webpage_url'],
            'channel': entry['channel'],
            'duration': verbouse_time_from_seconds(entry['duration']),
            'source': entry['formats'][0]['url']
            } for entry in entries]

    def next_song(self):
        if self.vc is None or not self.vc.is_connected():
            self.music_queue = []

        if len(self.music_queue) > 0:
            song = self.music_queue.pop(0)
            self.vc.play(self._generate_audiosource(song['source']), after=lambda e: self.next_song())

    async def play_music(self, ctx):
        if self.vc is None or not self.vc.is_connected():
            await ctx.author.voice.channel.connect()
            self.vc = ctx.voice_client
        
        if self.vc.is_playing() or self.vc.is_paused() or len(self.music_queue) == 0:
            if len(self.music_queue) > 0:
                song = self.music_queue[-1]
                embed = discord.Embed(title=None, description=f"Added [{song['title']}]({song['web_url']}) to the queue!", color=1675392)
                await ctx.send(embed=embed)
            return
        
        song = self.music_queue.pop(0)
        
        self.vc.play(self._generate_audiosource(song['source']), after=lambda e: self.next_song())


    @commands.command(name='play', aliases=["p"])
    async def play(self, ctx, *args):
        query = " ".join(args)
        
        if not query and self.vc is not None and self.vc.is_paused():
            self.vc.resume()
            return
        elif not query:
            await ctx.send("Searching for notihing...")
            await ctx.send("Hmm... can't find anything...")
            await ctx.send("Oh nice! I found nothing!")
            return

        author_voice = ctx.author.voice

        if author_voice is None:
            await ctx.send("What's the point in playing music if you are not in any voice channel?")
            return
        elif self.vc is not None and self.vc.channel.id != author_voice.channel.id:
            await ctx.send("Won't do it. It seems like we are not on the same channel.")
            return
        elif not query and self.vc is not None and self.vc.is_paused():
            self.vc.resume()
            return
        
        if self.confirmation_list is None:
            search = query + "..."
            is_url = False
            if valid_url(query):
                search = f'<{query}>'
                is_url = True
            
            await ctx.send(f"Searching for {search}") 

            songs = self.search_yt(query)

            if songs == False: # "not song" is also true for empty list ({})
                await ctx.send("Could not find the songs. Try another query. If its an URL it must start with 'https:// and point to a youtube video'")
                return
            
            if is_url:
                self.music_queue.append(songs[0])
                await self.play_music(ctx)
                return

            self.confirmation_list = songs
            await ctx.send(embed=self._generate_embed(songs))

            return
        
        try:
            song_num = int(query)
        except ValueError:
            if query == 'cancel':
                self.confirmation_list = None
                await ctx.send("Cancelled the search.")
                return
            await ctx.send("Not a valid option number. Send '?play cancel' if you want to cancel current search.")
            return
        if song_num <= 0 or song_num > len(self.confirmation_list):
            await ctx.send("Not a valid option number. Send '?play cancel' if you want to cancel current search.")
            return
        
        self.music_queue.append(self.confirmation_list[song_num-1])
        self.confirmation_list = None
        await self.play_music(ctx)

    @commands.command(name='skip', aliases=["s"])
    async def skip(self, ctx):
        if self.vc is None or not self.vc.is_connected():
            await ctx.send("I'm not connected to any VC")
            return
        if not self.vc.is_playing() and not self.vc.is_paused():
            await ctx.send("I'm not playing anything right now")
            return

        self.vc.stop()
    
    @commands.command(name='pause')
    async def pause(self, ctx):
        if self.vc is None or not self.vc.is_connected():
            await ctx.send("I'm not connected to any VC")
            return
        if not self.vc.is_playing() and not self.vc.is_paused():
            await ctx.send("I'm not playing anything right now")
            return
        if self.vc.is_paused():
            await ctx.send("Already pasused")
            return

        self.vc.pause()
    
    @commands.command(name='disconnect', alisase=['disc', 'fuckoff', 'exit'])
    async def disconnect(self, ctx):
        if ctx.voice_client:
            self.vc = None
            self.music_queue = []
            self.confirmation_list = None
            await ctx.voice_client.disconnect()
    

    @staticmethod
    def _generate_embed(search_results):
        embed = discord.Embed(
            title="Search Resutls",
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            color=1675392,
            description="Choose one of the songs below and send the \"play\" command with the number of the song. \n\nExample: ?play 2\n\n"
        )
        for i, song in enumerate(search_results):
            embed.add_field(
                name=f'{i+1}: {song["title"]} - [{song["channel"]}]',
                value=f'Duration: {song["duration"]}\nURL: {song["web_url"]}',
                inline=False
            )
        return embed

    def _generate_audiosource(self, url):
        exe_path = None
        if platform == "linux" or platform == "linux2":
            exe_path = "/usr/bin/ffmpeg"
        elif platform == "win32" or platform == "win64":
            exe_path = 'ffmpeg/bin/ffmpeg.exe'
        
        return discord.FFmpegPCMAudio(url, executable=exe_path, **self.FFMPEG_OPTIONS)

async def play_file(ctx, path):
    exe_path = None
    if platform == "linux" or platform == "linux2":
        exe_path = "/usr/bin/ffmpeg"
    elif platform == "win32" or platform == "win64":
        exe_path = 'ffmpeg/bin/ffmpeg.exe'

    if not exe_path:
        ctx.channel.send("Something went wrong, I am unable to reproduce audio")
        return

    vc = ctx.author.voice.channel
    voice = ctx.voice_client
    if not voice:
        await vc.connect()
        voice = ctx.voice_client

    voice.play(discord.FFmpegPCMAudio(executable=exe_path, source=path))


@client.command()
async def purei(ctx):
    await play_file(ctx, 'assets/nggyu.mp3')


@client.command(aliases=['rap'])
async def katsurap(ctx):
    await play_file(ctx, 'bot/assets/katsurap.mp3')





@client.command()
async def connectvc(ctx):
    vc = ctx.author.voice.channel
    await vc.connect()
