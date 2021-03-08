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


@bot.command()
async def servers(ctx):
	servers = list(bot.guilds)
	await ctx.send(f"Connected on {len(servers)} servers:")
	await ctx.send('\n'.join(server.name for server in servers))

@bot.command()
async def github(ctx):
	await ctx.send("https://github.com/dsjong/metamon")

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
		return str(reaction.emoji) in ['◀️', '▶️'] and reaction.message == msg and user == ctx.author

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

@bot.command(aliases=["evo"])
async def evolutions(ctx, *, args):
	poke_id = row_from(name_cols, args)
	if poke_id == -1:
		await ctx.send(f"Could not find a pokemon matching `{args}`")
		return

	vis = {poke_id: 4}
	def dfs(x):
		for y in [int(t) for t in str((row_to(["evo.to"], x)+[-1])[0]).split()]:
			if y in vis or y == -1: continue
			vis[y] = vis[x]+1
			dfs(y)
		for y in [int(t) for t in str((row_to(["evo.from"], x)+[-1])[0]).split()]:
			if y in vis or y == -1: continue
			vis[y] = vis[x]-1
			dfs(y)

	dfs(poke_id)

	embed=discord.Embed(title="Evolution Family")
	cnt = 1
	def megas(x: int):
		exists = [bool(str(x)) for x in row_to(mega_cols, x)] + [0, 0]
		if sum(exists) == 0: return ''
		ans = ' ('
		if exists[0]: ans += "Mega"
		if exists[1]: ans += "Mega X, Y"
		ans += ')'
		return ans

	for stage in range(1, 10):
		gen = [''.join(row_to(["name.en"], x)) for x in vis if vis[x] == stage]
		mega = [megas(x) for x in vis if vis[x] == stage]
		gen_mega = [''.join(x) for x in zip(gen, mega)]
		if gen:
			embed.add_field(name=f"Stage {cnt}", value="\n".join(gen_mega), inline=True)
			cnt += 1
	await ctx.send(embed=embed)

#----------construction----------
'''
@bot.command(aliases=["bulb"])
async def bulbapedia(ctx, *, args):
	await ctx.send(f"https://bulbapedia.bulbagarden.net/wiki/{args.replace(' ', '_')}_(Pok%C3%A9mon)")
'''
bot.run(os.environ['TOKEN'])
