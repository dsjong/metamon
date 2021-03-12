import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
from time import time
from itertools import cycle
from fetch import *
from constants import *

load_dotenv('.env')

bot = commands.Bot(command_prefix='p!')

#----------Bot-related commands----------
@bot.event
async def on_ready():
	global transform_time
	transform_time = -1
	print('Logged in as')
	print(bot.user.name)
	print(bot.user.id)
	cute = cycle(["Mew", "Pikachu", "Eevee"])
	for player in cute:
		discord_status = discord.Activity(type=discord.ActivityType.playing, name = "with " + player)
		await bot.change_presence(activity = discord_status)
		await asyncio.sleep(300)

@bot.command(brief="Play table tennis!")
async def ping(ctx):
	latency = round(bot.latency*1000)
	await ctx.send('Pong! `{0} ms`'.format(latency))

@bot.command(brief="List servers Metamon is in")
async def servers(ctx):
	servers = list(bot.guilds)
	await ctx.send(f"Connected on {len(servers)} servers:")
	await ctx.send('\n'.join(server.name for server in servers))

@bot.command(brief="See my code 👀")
async def github(ctx):
	await ctx.send("https://github.com/dsjong/metamon")

@bot.command(brief="Ask Metamon to transform!")
@from_args
async def transform(ctx, *, args=None):
	global transform_time
	if transform_time != -1:
		await ctx.send(f"Ditto is still transformed! `{600 - round(time() - transform_time)}` seconds until revert.")
		return
	poke_row, shiny = args
	poke_id, name = row_to(["id", "name.en"], poke_row)
	if name == "Bruxish":
		await ctx.send("Come on now. Really?")
		return
	with open(Path(__file__).parent / "data" / ("shiny" if shiny else "images") / f"{poke_id}.png", 'rb') as img:
		transform_time = time()
		pfp = img.read()
		await bot.user.edit(avatar=pfp)
		await ctx.send(f"Ditto transformed into {name}!")
		await asyncio.sleep(600)
		transform_time = -1
		pfp = open(Path(__file__).parent / "data" / "images" / f"132.png", 'rb').read()
		await bot.user.edit(avatar=pfp)
		await ctx.send(f"Ditto went back to its original form...")

#----------Pokemon info commands----------

@bot.command(aliases=["weak"], brief="Type effectiveness of defending pokemon/type")
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

@bot.command(aliases=["cover"], brief="Type effectiveness of attacking type")
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

@bot.command(brief="Type of selected pokemon")
@from_args
async def type(ctx, *, args=None):
	poke_row, shiny = args
	await ctx.send(', '.join(row_to(type_cols, poke_row)))

@bot.command(brief="Base stats of selected pokemon")
@from_args
async def stats(ctx, *, args=None):
	poke_row, shiny = args
	base_stats = row_to(stat_cols, poke_row)
	stat_names = ["HP", "ATK", "DEF", "SATK", "SDEF", "SPD"]
	dex, name = row_to(["dex_number", "name.en"], poke_row)
	bars = 14
	def field(stat):
		ret = [' ' for _ in range(3-len(stat))] + [stat]
		return ''.join(ret)

	def bar(stat: int):
		ret = ["```yaml\n", field(str(stat)), " "]
		fill = (stat*bars+254)//255
		blank = bars - fill
		ret += ["█" for _ in range(fill)]
		ret += [" " for _ in range(blank)]
		ret += "```"
		return ''.join(ret)
	embed = discord.Embed(title=f"#{dex} {name}")
	for i in range(6):
		embed.add_field(name=stat_names[i], value=bar(base_stats[i]), inline=True)
	embed.add_field(name=f"Base Stat Total: {sum(base_stats)}", value=f"[Other Pokémon with this total](https://bulbapedia.bulbagarden.net/wiki/Category:Pokémon_with_a_base_stat_total_of_{sum(base_stats)})", inline=False)
	await ctx.send(embed=embed)

@bot.command(brief="Translate a Pokemon name", help="Available languages: en, ja, ja_r, ja_t, de, fr")
@from_args
async def translate(ctx, arg, *, args=None):
	poke_row, shiny = args
	await ctx.send(''.join(row_to(["name."+arg], poke_row)))

@bot.command(brief="Pokemon name at the tip of your tongue?")
async def regex(ctx, *, args=None):
	if args == None:
		ctx.send("No arguments supplied!")
		return
	poke_row = row_from(["name.en"], args, True)
	if(poke_row == -1):
		await ctx.send(f"Could not find a pokemon matching `{args}`")
		return
	msg = await ctx.send(''.join(row_to(["name.en"], poke_row)))
	await msg.add_reaction('◀️')
	await msg.add_reaction('▶️')
	
	def check(reaction, user):
		return str(reaction.emoji) in ['◀️', '▶️'] and reaction.message == msg and user == ctx.author

	while True:
		reaction, user = await bot.wait_for('reaction_add', check=check)
		if (str(reaction.emoji)[0] == '▶'):
			await msg.remove_reaction(reaction, user)
			tmp = row_from(["name.en"], args, True, poke_row+1, 1)
			if(tmp != -1):
				poke_row = tmp
				await msg.edit(content=''.join(row_to(["name.en"], poke_row)))
		else:
			await msg.remove_reaction(reaction, user)
			tmp = row_from(["name.en"], args, True, poke_row-1, -1)
			if(tmp != -1):
				poke_row = tmp
				await msg.edit(content=''.join(row_to(["name.en"], poke_row)))

@bot.command(brief="Definitely not a Poketwo cheat...")
async def hint(ctx, *, args=None):
	if args == None:
		ctx.send("No arguments supplied!")
		return
	args = ''.join(['^', args.replace('_', '.'), '$'])
	await ctx.invoke(bot.get_command('regex'), args=args)

@bot.command(aliases=["evo"], brief="Evolution family of selected pokemon")
@from_args
async def evolutions(ctx, *, args=None):
	poke_row, shiny = args
	vis = {poke_row: 4}
	def dfs(x):
		for y in [int(t) for t in str((row_to(["evo.to"], x)+[-1])[0]).split()]:
			if y in vis or y == -1: continue
			vis[y] = vis[x]+1
			dfs(y)
		for y in [int(t) for t in str((row_to(["evo.from"], x)+[-1])[0]).split()]:
			if y in vis or y == -1: continue
			vis[y] = vis[x]-1
			dfs(y)

	dfs(poke_row)

	embed=discord.Embed(title="Evolution Family")
	cnt = 1
	def megas(x: int):
		exists = [True for _ in row_to(mega_cols, x)] + [False, False]
		if sum(exists) == 0: return ''
		ans = ' (Mega'
		if row_to(mega_cols[1:2], x): ans += " X, Y"
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

@bot.command(aliases=["img"], brief="Image of selected pokemon")
@from_args
async def image(ctx, *, args=None):
	poke_row, shiny = args
	poke_id = row_to(["id", "name.en"], poke_row)[0]
	with open(Path(__file__).parent / "data" / ("shiny" if shiny else "images") / f"{poke_id}.png", 'rb') as img:
		await ctx.send(file=discord.File(img))

#----------construction----------
'''
@bot.command(aliases=["bulb"])
async def bulbapedia(ctx, *, args):
	await ctx.send(f"https://bulbapedia.bulbagarden.net/wiki/{args.replace(' ', '_')}_(Pok%C3%A9mon)")
'''
bot.run(os.environ['TOKEN'])
