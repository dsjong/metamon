import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
from itertools import cycle
from fetch import *
from constants import *

load_dotenv('.env')

bot = commands.Bot(command_prefix='p!')

@bot.event
async def on_ready():
	print('Logged in as')
	print(bot.user.name)
	print(bot.user.id)
	cute = cycle(["Mew", "Pikachu", "Eevee"])
	for player in cute:
		discord_status = discord.Activity(type=discord.ActivityType.playing, name = "with " + player)
		await bot.change_presence(activity = discord_status)
		await asyncio.sleep(300)

@bot.command()
async def ping(ctx):
	latency = round(bot.latency*1000)
	await ctx.send('Pong! `{0} ms`'.format(latency))

name_cols = ["slug", "name.ja", "name.ja_r", "name.ja_t", "name.en", "name.de", "name.fr"]
type_cols = ["type.0", "type.1"]
stat_cols = ["base.hp", "base.atk", "base.def", "base.satk", "base.sdef", "base.spd"]

@bot.command(aliases=["weak"])
async def weakness(ctx, *, args):
	# args is either pokemon name or type
	args = args[0].upper() + args[1:].lower()
	types = list(map(lambda x: TYPE_NUMBERS[x], row_to(type_cols, row_from(name_cols, args))))
	if (not types) and (args in TYPE_NUMBERS): types = [TYPE_NUMBERS[args]]
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

@bot.command(aliases=["cover"])
async def coverage(ctx, *, args):
	args = args[0].upper() + args[1:].lower()
	types = []
	if args in TYPE_NUMBERS: types = [TYPE_NUMBERS[args]]
	if not types:
		await ctx.send(f"Could not find a type matching `{args}`")
		return
	weaknesses, resistances, immunities = [], [], []
	for i in range(1, len(TYPES)):
		typ_mult = 1
		for j in types: typ_mult *= TYPE_EFFICACY[j][i]
		def bolden(x):
			return ''.join(['**', x, '**']) if (typ_mult==0.25 or typ_mult==4) else x
		if typ_mult == 0: immunities += [bolden(TYPES[i])]
		elif typ_mult > 1: weaknesses += [bolden(TYPES[i])]
		elif typ_mult < 1: resistances += [bolden(TYPES[i])]
	await ctx.send(
		f"Super effective: {', '.join(weaknesses)}\n" +
		f"Resists: {', '.join(resistances)}\n" +
		f"Immunities: {', '.join(immunities)}\n"
	)

@bot.command()
async def type(ctx, *, args):
	poke_id = row_from(name_cols, args)
	if poke_id == -1:
		await ctx.send(f"Could not find a pokemon matching `{args}`")
		return
	else: await ctx.send(', '.join(row_to(type_cols, poke_id)))

@bot.command()
async def stats(ctx, *, args):
	poke_id = row_from(name_cols, args)
	if poke_id == -1:
		await ctx.send(f"Could not find a pokemon matching `{args}`")
		return
	base_stats = row_to(stat_cols, poke_id)
	#dex, name = row_to([dex_number, name.en], poke_id)
	#embed = discord.Embed(title=f"#{dex} {name}")
	await ctx.send(
		f"HP: {base_stats[0]}\n" +
		f"ATK: {base_stats[1]}\n" +
		f"DEF: {base_stats[2]}\n" +
		f"SATK: {base_stats[3]}\n" +
		f"SDEF: {base_stats[4]}\n" +
		f"SPD: {base_stats[5]}\n" +
		f"**Total: {sum(base_stats)}**\n"
	)

@bot.command()
async def translate(ctx, arg, *, args):
	poke_id = row_from(name_cols, args)
	if poke_id == -1:
		await ctx.send(f"Could not find a pokemon matching `{args}`")
		return
	await ctx.send(''.join(row_to(["name."+arg], poke_id)))

@bot.command()
async def regex(ctx, *, args):
	poke_id = row_from(["name.en"], args, True)
	if(poke_id == -1):
		await ctx.send(f"Could not find a pokemon matching `{args}`")
		return
	msg = await ctx.send(''.join(row_to(["name.en"], poke_id)))
	await msg.add_reaction('◀️')
	await msg.add_reaction('▶️')
	
	def check(reaction, user):
		return str(reaction.emoji) in ['◀️', '▶️'] and reaction.message == msg and user==ctx.author

	while True:
		reaction, user = await bot.wait_for('reaction_add', check=check)
		if (str(reaction.emoji)[0] == '▶'):
			tmp = row_from(["name.en"], args, True, poke_id+1, 1)
			if(tmp != -1):
				poke_id = tmp
				await msg.edit(content=''.join(row_to(["name.en"], poke_id)))
		else:
			tmp = row_from(["name.en"], args, True, poke_id-1, -1)
			if(tmp != -1):
				poke_id = tmp
				await msg.edit(content=''.join(row_to(["name.en"], poke_id)))

@bot.command()
async def hint(ctx, *, args):
	args = ''.join(['^', args.replace('_', '.'), '$'])
	await ctx.invoke(bot.get_command('regex'), args=args)

@bot.command()
async def servers(ctx):
	servers = list(bot.guilds)
	await ctx.send(f"Connected on {str(len(servers))} servers:")
	await ctx.send('\n'.join(server.name for server in servers))
'''
@bot.event
async def on_message(message):
	if message.content.startswith('$thumb'):
		channel = message.channel
		msg = await channel.send('Send me that 👍 reaction, mate')

		def check(reaction, user):
			return user == message.author and str(reaction.emoji) == '👍' and reaction.message == msg

		try:
			reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
		except asyncio.TimeoutError:
			await channel.send('👎')
		else:
			await channel.send('👍')
'''

bot.run(os.environ['TOKEN'])