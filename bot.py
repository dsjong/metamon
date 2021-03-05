import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from fetch import *
from constants import *

load_dotenv('.env')

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

@bot.command(aliases=["weak"])
async def weakness(ctx, *, args):
	# args is either pokemon name or type
	args = args[0].upper() + args[1:].lower()
	types = []
	if id_from_name(args) != -1: types = list(map(lambda x: TYPE_NUMBERS[x], types_from_name(args)))
	elif args in TYPE_NUMBERS: types = [TYPE_NUMBERS[args]]
	if not types:
		await ctx.send(f"Could not find a pokemon or type matching `{args}`")
		return
	weaknesses, resistances, immunities = [], [], []
	for i in range(1, len(TYPES)):
		typ_mult = 1
		for j in types: typ_mult *= TYPE_EFFICACY[i][j]
		def bolden(x):
			return ''.join(['**', x, '**']) if (typ_mult==0.25 or typ_mult==4) else x
		if typ_mult == 0: immunities += [bolden(TYPES[i])]
		elif typ_mult > 1: weaknesses += [bolden(TYPES[i])]
		elif typ_mult < 1: resistances += [bolden(TYPES[i])]
	await ctx.send(
		f"Weaknesses: {', '.join(weaknesses)}\n" +
		f"Resistances: {', '.join(resistances)}\n" +
		f"Immunities: {', '.join(immunities)}\n"
	)

@bot.command()
async def type(ctx, *, args):
	poke_id = id_from_name(args)
	await ctx.send(f"Could not find a pokemon matching `{args}`" if poke_id == -1 else ', '.join(types_from_id(poke_id)))

bot.run(os.getenv('TOKEN'))