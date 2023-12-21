import discord
from discord.ext import commands
import yt_dlp
import json
import asyncio
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

#Чтение токена
def read_token(filename='config.json'):
    with open(filename, 'r') as file:
        config = json.load(file)
    return config

config_data = read_token()
bot_token = config_data.get('bot_token','1')
SPOTIPY_CLIENT_ID = config_data.get('spotify_client_id','1')
SPOTIPY_CLIENT_SECRET = config_data.get('spotify_client_secret', '1')
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET))

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
#Пустой список для очереди
queue = []
loop_on = False

ffmpeg_options = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn',
                }

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def play(ctx, url):
    voice_channel = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    channel = ctx.author.voice.channel
    # Есть ли бот в каком-либо канале
    if voice_channel is None: #Бота нет ни в одном канале
        await channel.connect()
        voice_channel = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    elif str(voice_channel.channel.name).strip() is not str(channel).strip(): #Бот в другом канале
        await voice_channel.disconnect()
        await channel.connect()

    ydl = yt_dlp.YoutubeDL({
        'format': 'bestaudio/best',
        'postprocessors': [{
		'key': 'FFmpegExtractAudio',
		'preferredcodec': 'mp3',
		'preferredquality': '192',
		}],
	})

    global queue
    
    try:
        info = ydl.extract_info(url, download=False)
    except yt_dlp.utils.DownloadError:
        try:
            await splay(ctx, url = url)
            return
        except spotipy.exceptions.SpotifyException:
            await saplay(ctx, url = url)
            return

    try:
        for urls in info['entries']:
            queue.append(urls['webpage_url'])
    except KeyError:
        queue.append(url)
    voice_channel = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice_channel.is_playing(): #Если он ничего не играет
        await next(ctx)
        return
 
async def next(ctx):
    global queue
    if queue:
        ydl = yt_dlp.YoutubeDL({
            'format': 'bestaudio/best',
		    'postprocessors': [{
		    'key': 'FFmpegExtractAudio',
		    'preferredcodec': 'mp3',
		    'preferredquality': '192',
		    }],
	    })

        voice_channel = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        # Используем yt-dlp для получения музыкальной информации
        url = queue.pop(0)
        info = ydl.extract_info(url, download=False)
        url2 = info['url']
        #Достаем название ссылки и пишем в чате
        video_title = info['title']
        await ctx.send(f'Играет: {video_title}')
        
        voice_channel.play(discord.FFmpegPCMAudio(url2, **ffmpeg_options), after=lambda e: for_loop(ctx,url2))

        #Ждем пока играет
        while voice_channel.is_playing():
            await asyncio.sleep(1)
        #Запускает следующее в очереди
        try:
            if queue[0] is not None:
                await next(ctx)
        except IndexError:
            bot.loop.create_task(check_playing_music(ctx))            
            
        
@bot.command()
async def skip(ctx):
    voice_channel = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_channel is None:
        await ctx.send('Я не там где нужно')
        return
    elif not voice_channel.is_playing():
        await ctx.send('Ничего не играет')
        return
    voice_channel.stop()
    #await next(ctx)

@bot.command()
async def clean(ctx):
    global queue
    queue = []

async def check_playing_music(ctx):
    await asyncio.sleep(300)
    voice_channel = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_channel.is_playing():
        return
    else:
        await voice_channel.disconnect()
        await ctx.send(f'Нет друзей...')
        print(f'Нет друзей...')

def for_loop(ctx, url):
    global loop_on
    if loop_on:
        voice_channel = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        voice_channel.play(discord.FFmpegPCMAudio(url, **ffmpeg_options), after=lambda e: for_loop(ctx,url))
    else:
        bot.loop.create_task(check_playing_music(ctx))            

@bot.command()
async def loop(ctx):
    global loop_on
    loop_on = not loop_on
    await ctx.send(f'Повтор трека {"вкл" if loop_on else "выкл"}')

@bot.command()
async def search(ctx, *, name_song):
    channel = ctx.author.voice.channel
    voice_channel = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    
    ydl = yt_dlp.YoutubeDL({
        'format': 'bestaudio/best',
        'postprocessors': [{
	    'key': 'FFmpegExtractAudio',
	    'preferredcodec': 'mp3',
        'preferredquality': '192',
	    }],
        'noplaylist': True,
    })
    search_results = ydl.extract_info(f'ytsearch5:{name_song}', download = False)['entries']

    if not search_results:
        await ctx.send('Ничего нет по запросу')
        return
    print(search_results[0]['webpage_url'])
    options = [f"{i+1}. {result['title']}" for i, result in enumerate(search_results)]
    options_message = "\n".join(options)

    await ctx.send(f"Выбрать:\n{options_message}")
    
    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel and message.content.isdigit() and 1 <= int(message.content) <= 5

    try:
        response = await bot.wait_for('message', check=check, timeout=30)
        selected_index = int(response.content) - 1
        selected_video = search_results[selected_index]
        video_url = selected_video['webpage_url']
    except (ValueError, IndexError, asyncio.TimeoutError):
        await ctx.send("Поздно или не то")
        return

    await play(ctx,video_url)

async def splay(ctx, url):
    name_track = sp.track(url)['name']
    name_artist = sp.track(url)['artists'][0]['name']
    name_song = str(name_track + ' ' + name_artist)
    await search_song(ctx, name_song = name_song)

async def search_song(ctx, *, name_song):
    global queue
    channel = ctx.author.voice.channel
    voice_channel = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    
    ydl = yt_dlp.YoutubeDL({
        'format': 'bestaudio/best',
        'postprocessors': [{
	    'key': 'FFmpegExtractAudio',
	    'preferredcodec': 'mp3',
        'preferredquality': '192',
	    }],
        'noplaylist': True,
    })
    search_video = ydl.extract_info(f'ytsearch1:{name_song}', download = False)['entries']
    video_url = search_video[0]['webpage_url']
    
    queue.append(video_url)

async def saplay(ctx, url):
    album_info = sp.album_tracks(url)
    urls_from_album_info = album_info['items'][0]['external_urls']['spotify']
    voice_channel = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    for url in album_info['items']:
        #print(url['external_urls']['spotify'])
        await splay(ctx, url = url['external_urls']['spotify'])
    if not voice_channel.is_playing(): #Если он ничего не играет
       await next(ctx)
       return
    
    #print(urls_from_album_info)

#Запускаем бота
bot.run(bot_token)
