import discord
from discord.ext import commands

class Battle(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.user1
		self.user2
		if not hasattr(self.bot, "battles"):
			self.bot.battles = BattleManager()

	@commands.group(help="Play ELO-rated rock paper scissors")
	async def battle(self, ctx, *, args: discord.Member):
		if args == ctx.author:
			print("An attempt was made...")

		if args in self.bot.battle

class BattleManager():
	def __init__(self):
		self.battles = {}

	def __contains__(self, user):
		return user.id in self.battles

	def new(self, user1, user2, ctx):
		battle = Battle([user1, user2], ctx, self)
		self.battles[user1.id] = battle
		self.battles[user2.id] = battle
		return battle