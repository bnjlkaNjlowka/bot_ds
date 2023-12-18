import discord
from discord.ext import commands
import yt_dlp
import json

#Чтение токена
def read_token(filename='config.json'):
    with open(filename, 'r') as file:
        config = json.load(file)
    return config

config_data = read_token()
bot_token = config_data.get('bot_token','1')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
#Пустой список для очереди
queue = []

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

    queue.append(url)
    voice_channel = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if not voice_channel.is_playing(): #Если он ничего не играет
        await next(ctx)
 
async def next(ctx):
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
	
        voice_channel.play(discord.FFmpegPCMAudio(url2), after=lambda e: print('done', e))
        voice_channel.source = discord.PCMVolumeTransformer(voice_channel.source)
        voice_channel.source.volume = 0.07

@bot.command()
async def skip(ctx):
    voice_channel = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_channel is None:
        await ctx.send('Я не там где нужно')
        return
    elif not voice_channel.is_playing():
        await('Ничего не играет')
        return

    voice_channel.stop()

    await next(ctx)


#Запускаем бота
bot.run(bot_token)
