import csv
from collections import defaultdict
from pathlib import Path
from typing import List
import constants
import re
import inspect
from constants import *


#----------decorators----------
def from_args(func):
	async def wrapper(*args, **kwargs):
		ctx = args[0]
		if kwargs["args"] == None:
			await ctx.send("No arguments supplied!")
			return
		poke_name, shiny = kwargs["args"].lower(), False
		if poke_name.startswith("shiny"):
			poke_name = poke_name[5:].strip()
			shiny = True
		poke_row = row_from(name_cols, poke_name)
		if poke_row == -1 or (not row_to(["enabled"], poke_row)):
			await args[0].send(f"Could not find a pokemon matching `{kwargs['args']}`")
			return
		await func(*args, args=[poke_row, shiny])
	wrapper.__name__ = func.__name__
	wrapper.__signature__ = inspect.signature(func)
	return wrapper

def isnumber(v):
	try: int(v)
	except ValueError: return False
	return True

def get_data_from(filename):
	path = Path(__file__).parent / "data" / "csv" / filename
	with open(path) as f:
		reader = csv.DictReader(f)
		data = [None] + list({k: int(v) if isnumber(v) else v for k, v in row.items() if v!=""} for row in reader)
	return data

#----------pokemon.csv----------
def row_from(cols: List[str], value, regex=False, start=1, jump=1):
	file = get_data_from("pokemon.csv")
	for i in range(start, len(file) if jump==1 else 0, jump):
		for j in cols:
			def cmp(str1: str, str2: str):
				if regex: return re.search(str1, str2)
				return str1 == str2
			if cmp(str(value).lower(), str(file[i].get(j, "__NULL__")).lower()): return i
	return -1

def row_to(cols: List[str], row):
	if(row == -1): return []
	file = get_data_from("pokemon.csv")
	return [value for value in (file[row].get(x, None) for x in cols) if value != None]
