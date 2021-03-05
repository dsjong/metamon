import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv('discord.env')

bot = commands.Bot(command_prefix='p!')

@bot.event
async def on_ready():
	print('Logged in as')
	print(bot.user.name)
	print(bot.user.id)

@bot.command()
async def ping(ctx):
	latency = round(bot.latency*1000)
	await ctx.send('Pong! `{0} ms`'.format(latency))

bot.run(os.getenv('TOKEN'))