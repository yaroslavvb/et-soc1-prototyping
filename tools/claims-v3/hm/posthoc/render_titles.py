"""Copies of the session protocols with plain, short block titles for the movie frames (the registered titles stay
in prereg/; only the words drawn on the movies change). Usage: render_titles.py <protocol in> <protocol out>"""
import json
import sys

TITLES = {
    "E62-ORBIT": "Heat walks the die's four corners, then the centre",
    "E62-BLOOM": "The whole chip on, then off: the board warms and cools",
    "E62-WE42": "Twelve shires west, then twelve east: the heat follows",
    "E62-NS42": "The same shires split north and south: the heat turns",
    "E62-NULLAA": "Control: the same twelve shires in both phases",
    "E62-NULLGEO": "Control: twelve shires against their rotated copy",
    "E62-W8BE8B": "Replicate: eight shires west, then eight east",
    "E62-SWEEP": "A block of work slides across the die, column by column",
}
p = json.load(open(sys.argv[1]))
for b in p["blocks"]:
    if b.get("id") in TITLES:
        b["title"] = TITLES[b["id"]]
json.dump(p, open(sys.argv[2], "w"), indent=1)
print("titles set:", [b["id"] for b in p["blocks"] if b.get("id") in TITLES])
