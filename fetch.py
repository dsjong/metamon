import csv
from collections import defaultdict
from pathlib import Path
import constants

def isnumber(v):
	try: int(v)
	except ValueError: return False
	return True

def get_data_from(filename):
	path = Path(__file__).parent / "data" / filename
	with open(path) as f:
		reader = csv.DictReader(f)
		data = list({k: int(v) if isnumber(v) else v for k, v in row.items() if v!=""} for row in reader)
	return data

def id_from_name(name: str):
	name = name.lower()
	for row in get_data_from("pokemon.csv"):
		if(row["slug"] == name): return row["id"]
	return -1

def types_from_id(id: int):
	id -= 1
	file = get_data_from("pokemon.csv")
	try: return (file[id]["type.0"],) + (file[id]["type.1"],)
	except KeyError: return (file[id]["type.0"],)

def types_from_name(name: str):
	return types_from_id(id_from_name(name))