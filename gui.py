import discord
from discord.ext import commands
import utils
import music

class Button(discord.ui.View):
    def __init__(self, ctx, bot, name_video):
        super().__init__()
        self.ctx = ctx
        self.bot = bot
        self.name_video = name_video
       
    @discord.ui.button(label = 'Пауза', style = discord.ButtonStyle.blurple)
    async def pause_button(self, interaction: discord.Interaction, Button: discord.ui.Button):
        await interaction.response.edit_message(content = f'Играет: {self.name_video} Пауза')
        await utils.pause(ctx = self.ctx, bot = self.bot)
    @discord.ui.button(label = 'Возобновить')
    async def resume_button(self, interaction: discord.Interaction, Button: discord.ui.Button):
        await interaction.response.edit_message(content = f'Играет: {self.name_video}')
        await utils.resume(ctx = self.ctx, bot = self.bot)
    @discord.ui.button(label = 'Следующий')
    async def next_button(self, interaction: discord.Interaction, Button: discord.ui.Button):
        await interaction.response.defer()
        await utils.skip(ctx = self.ctx, bot = self.bot)
    @discord.ui.button(label = 'Повтор')
    async def loop_button(self, interaction: discord.Interaction, Button: discord.ui.Button):
        await interaction.response.defer()
        await music.loop(ctx = self.ctx, bot = self.bot)

class SelectMenu(discord.ui.Select):
    def __init__(self, search_results, ctx, bot):
        options = [discord.SelectOption(label ='1.' + str(search_results[0]['title'])),
                   discord.SelectOption(label ='2.' + str(search_results[1]['title'])),
                   discord.SelectOption(label ='3.' + str(search_results[2]['title'])),
                   discord.SelectOption(label ='4.' + str(search_results[3]['title'])),
                   discord.SelectOption(label ='5.' + str(search_results[4]['title']))]
        super().__init__(options = options)
        self.ctx = ctx
        self.bot = bot
        self.search_results = search_results
    
    async def callback(self, interaction: discord.Interaction):
        if self.values[0][0] == '1':
            await interaction.response.defer()
            await music.for_next(ctx = self.ctx, url = self.search_results[0]['url'], name_song = self.search_results[0]['title'], bot = self.bot) 
        elif self.values[0][0] == '2':
            await interaction.response.defer()
            await music.for_next(ctx = self.ctx, url = self.search_results[1]['url'], name_song = self.search_results[0]['title'], bot = self.bot) 
        elif self.values[0][0] == '3':
            await interaction.response.defer()
            await music.for_next(ctx = self.ctx, url = self.search_results[2]['url'], name_song = self.search_results[0]['title'], bot = self.bot) 
        elif self.values[0][0] == '4':
            await interaction.response.defer()
            await music.for_next(ctx = self.ctx, url = self.search_results[3]['url'], name_song = self.search_results[0]['title'], bot = self.bot) 
        elif self.values[0][0] == '5':
            await interaction.response.defer()
            await music.for_next(ctx = self.ctx, url = self.search_results[4]['url'], name_song = self.search_results[0]['title'], bot = self.bot) 


class SelectMenuView(discord.ui.View):
    def __init__(self, ctx, bot, search_results):
        super().__init__()
        self.add_item(SelectMenu(ctx = ctx, bot = bot, search_results = search_results))

async def button(ctx, bot):
    await ctx.send(view = select_menu())
    #await utils.pause(ctx, bot = bot)
