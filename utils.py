import discord
from discord.ext import commands

#@commands.command()
async def pause(ctx, bot):
    voice_channel = discord.utils.get(bot.voice_clients, guild = ctx.guild)
    try:
        voice_channel.pause() 
    except AttributeError:
        await ctx.send('Не в канале')

async def resume(ctx, bot):
    voice_channel = discord.utils.get(bot.voice_clients, guild = ctx.guild)
    try:
        voice_channel.resume()
    except AttributeError:
        await ctx.send('Не в канале') 

async def skip(ctx, bot):
    voice_channel = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_channel is None:
        await ctx.send('Я не там где нужно')
        return
    elif not voice_channel.is_playing():
        await ctx.send('Ничего не играет')
        return
    voice_channel.stop()


