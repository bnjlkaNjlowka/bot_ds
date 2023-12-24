import discord
from discord.ext import commands
import yt_dlp
import json
import asyncio
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import gui

#Чтение токена
def read_token(filename='config.json'):
    with open(filename, 'r') as file:
        config = json.load(file)
    return config

config_data = read_token()
SPOTIPY_CLIENT_ID = config_data.get('spotify_client_id','1')
SPOTIPY_CLIENT_SECRET = config_data.get('spotify_client_secret', '1')
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET))

#Пустой список для очереди
queue = []
names_video = []
loop_on = False

ffmpeg_options = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn',
                }

ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
		'key': 'FFmpegExtractAudio',
		'preferredcodec': 'mp3',
		'preferredquality': '192',
		}],
	}

ydl = yt_dlp.YoutubeDL(ydl_opts)

async def connect(ctx, bot):
    voice_channel = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    channel = ctx.author.voice.channel
    if voice_channel is None: #Бота нет ни в одном канале
        await channel.connect()
    elif str(voice_channel.channel.name).strip() is not str(channel).strip(): #Бот в другом канале
        await voice_channel.disconnect()
        await channel.connect()

async def play(ctx, url, bot):
    global ydl      
    await ctx.message.delete()
    await connect(ctx, bot = bot)
    await get_url(ctx, url = url, bot = bot)
    voice_channel = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice_channel.is_playing(): #Если он ничего не играет
        await next(ctx, bot = bot)
        return

async def get_url(ctx, url, bot):
    global ydl
    global queue
    global names_video
    if str(url).find('youtube') != -1:
        if str(url).find('playlist') != -1:
            info = ydl.extract_info(url, download=False)
            for urls in info['entries']:
                queue.append(urls['url'])
                names_video.append(urls['title'])
        elif str(url).find('watch') != -1:
            info = ydl.extract_info(url, download=False)
            queue.append(info['url'])
            names_video.append(info['title'])
    elif str(url).find('open.spotify') != -1:
        if str(url).find('track') != -1:
            await splay(ctx, url = url, bot = bot)
        elif str(url).find('album') != -1:
            await saplay(ctx, url = url, bot = bot)
    else:
        await ctx.send('Ссылка невалидна. Только YouTube, Spotify.')

async def send_message(ctx, bot, name_video):
    global id_message
    video_title = name_video
    try:
        if id_message is not None:
            new_message = await ctx.channel.fetch_message(id_message)
            await new_message.edit(content = f'Играет: {video_title}', view = gui.Button(ctx = ctx, bot = bot, name_video = video_title))
    except Exception:
        message = await ctx.send(f'Играет: {video_title}', view = gui.Button(ctx = ctx, bot = bot, name_video = video_title))
        id_message = message.id     
        

async def next(ctx, bot):
    global queue
    global ydl
    global names_video
    global video_title
    if queue: 
        voice_channel = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        # Используем yt-dlp для получения музыкальной информации
        url = queue.pop(0)
        #Достаем название ссылки и пишем в чате
        video_title = names_video.pop(0)
        await send_message(ctx, bot = bot, name_video = video_title)
        voice_channel.play(discord.FFmpegPCMAudio(url, **ffmpeg_options), after = lambda e: for_loop(ctx, url = url, bot = bot))
        #Ждем пока играет
        while voice_channel.is_playing() or voice_channel.is_paused():
            await asyncio.sleep(1)
        #Запускает следующее в очереди
        try:
            if queue[0] is not None:
                await next(ctx, bot = bot)
        except IndexError:
            bot.loop.create_task(check_playing_music(ctx, bot))            

async def clean(ctx):
    global queue
    global names_video
    queue = []
    names_video = []

async def delete_message(ctx):
    global id_message
    new_message = await ctx.channel.fetch_message(id_message)
    await new_message.delete() 

async def check_playing_music(ctx, bot):
    await asyncio.sleep(10)
    voice_channel = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_channel.is_playing():
        return
    else:
        await voice_channel.disconnect()
        await delete_message(ctx)
        await ctx.send(f'Нет друзей...')
        print(f'Нет друзей...')

def for_loop(ctx, url, bot):
    global loop_on
    if loop_on:
        voice_channel = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        voice_channel.play(discord.FFmpegPCMAudio(url, **ffmpeg_options), after = lambda e: for_loop(ctx, url=url, bot = bot))
    else:
        bot.loop.create_task(check_playing_music(ctx, bot = bot)) 

async def loop(ctx, bot):
    global id_message
    global loop_on
    global video_title
    loop_on = not loop_on
    new_message = await ctx.channel.fetch_message(id_message)
    await new_message.edit(content = f'Играет: {video_title} {"Повтор трека вкл" if loop_on else ""}', view = gui.Button(ctx = ctx, bot = bot, name_video = video_title)) 

async def search(ctx, *, name_song, bot):
    channel = ctx.author.voice.channel
    voice_channel = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    search_results = ydl.extract_info(f'ytsearch5:{name_song}', download = False)['entries']
    if not search_results:
        await ctx.send('Ничего нет по запросу')
        return
    options = [f"{i+1}. {result['title']}" for i, result in enumerate(search_results)]
    options_message = "\n".join(options)
    await ctx.send(f"(Необходимо просто ввести цифру 1 - 5)\nВыбрать:\n{options_message}")
    
    def check(message):
        int(message.content)
        return message.author == ctx.author and message.channel == ctx.channel and message.content.isdigit() 

    try:
        response = await bot.wait_for('message', check=check, timeout=30)
        selected_index = int(response.content) - 1
        selected_video = search_results[selected_index]
        video_url = selected_video['url']
        name_video = selected_video['title']
        queue.append(video_url)
        names_video.append(name_video)
        await connect(ctx, bot = bot)
        voice_channel = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    except (ValueError, IndexError, asyncio.TimeoutError):
        await ctx.send("Невалидный ответ. Необходимо ввести цифру 1 - 5. Вводите заново !search 'запрос'.")
        return
    if not voice_channel.is_playing():
        await next(ctx, bot = bot)
        return

async def splay(ctx, url, bot):
    global names_video
    name_track = sp.track(url)['name']
    name_artist = sp.track(url)['artists'][0]['name']
    name_song = str(name_track + ' ' + name_artist)
    names_video.append(name_song)
    await search_song(ctx, name_song = name_song, bot = bot)

async def search_song(ctx, *, name_song, bot):
    global queue
    global ydl
    global names_video
    channel = ctx.author.voice.channel
    voice_channel = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    search_video = ydl.extract_info(f'ytsearch1:{name_song}', download = False)['entries']
    video_url = search_video[0]['url']
    queue.append(video_url)

async def saplay(ctx, url, bot):
    album_info = sp.album_tracks(url)
    urls_from_album_info = album_info['items'][0]['external_urls']['spotify']
    voice_channel = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    for url in album_info['items']:
        await splay(ctx, url = url['external_urls']['spotify'], bot = bot)
    if not voice_channel.is_playing(): #Если он ничего не играет
        await next(ctx, bot = bot)
        return

