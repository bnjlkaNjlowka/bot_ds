import discord
from discord.ext import commands
import yt_dlp
import json

def read_token(filename='config.json'):
    with open(filename, 'r') as file:
        config = json.load(file)
    return config

config_data = read_token()
bot_token = config_data.get('bot_token','1')


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def play(ctx, url):
    voice_channel = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    channel = ctx.author.voice.channel
    # Есть ли бот в каком-либо канале
    if voice_channel is None:
        await channel.connect()
    else:
        await voice_channel.disconnect()
        await channel.connect()
    
    voice_channel = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    ydl = yt_dlp.YoutubeDL({
		'format': 'bestaudio/best',
		'postprocessors': [{
		'key': 'FFmpegExtractAudio',
		'preferredcodec': 'mp3',
		'preferredquality': '192',
		}],
	})

    # Используем yt-dlp для получения музыкальной информации
    info = ydl.extract_info(url, download=False)
    url2 = info['url']
	
    voice_channel.play(discord.FFmpegPCMAudio(url2), after=lambda e: print('done', e))
    voice_channel.source = discord.PCMVolumeTransformer(voice_channel.source)
    voice_channel.source.volume = 0.07
# Запускаем бота
bot.run(bot_token)
