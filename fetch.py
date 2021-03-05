import csv
from collections import defaultdict
from pathlib import Path
from typing import List
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

def row_from(cols: List[str], value):
	file = get_data_from("pokemon.csv")
	for i in range(0, len(file)):
		for j in cols:
			if str(file[i].get(j, "__NULL__")).lower() == str(value).lower(): return i
	return -1

def row_to(cols: List[str], row):
	if(row == -1): return []
	file = get_data_from("pokemon.csv")
	return [value for value in (file[row].get(x, None) for x in cols) if value != None]