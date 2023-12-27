import discord
from discord.ext import commands
import json
import utils
import music
import gui

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
async def pause(ctx):
    await utils.pause(ctx, bot = bot)

@bot.command()
async def resume(ctx):
    await utils.resume(ctx, bot = bot)

@bot.command()
async def play(ctx, url):
    await music.play(ctx, url = url, bot = bot)

@bot.command()
async def skip(ctx):
    await utils.skip(ctx, bot = bot)

@bot.command()
async def clean(ctx):
    await music.clean(ctx)

@bot.command()
async def search(ctx, *, name_song):
    await music.search(ctx, name_song = str(name_song), bot = bot)

@bot.command()
async def loop(ctx):
    await music.loop(ctx, bot = bot)

@bot.command()
async def menu(ctx):
    await gui.button(ctx, bot = bot) 

bot.run(bot_token)
