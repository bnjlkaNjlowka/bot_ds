import discord
from discord.ext import commands
import utils

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
    #@discord.ui.button(label = 'Следующий')
    #async def next_button(self, interaction: discord.Interaction, Button: discord.ui.Button):
    #    await interaction.response.edit_message(content =f'Играет {self.name_video}')
    #    await utils.skip(ctx = self.ctx, bot = self.bot)

async def button(ctx, bot):
    await ctx.send(view = Button(ctx = ctx, bot = bot))
    #await utils.pause(ctx, bot = bot)
