#!/usr/bin/env python

from __future__ import print_function
import argparse
import subprocess
import sys
import nbt2yaml
from PIL import Image, ImageDraw

p = argparse.ArgumentParser()
p.add_argument("villagefile")
p.add_argument("imagefile")
p.add_argument("--prerun")

args = p.parse_args()

if args.prerun:
   subprocess.call(args.prerun, shell=True)

try:
    with open(args.villagefile) as nbt:
        data = nbt2yaml.parse_nbt(nbt, True)
except IOError as e:
    print(e, file=sys.stderr)
    sys.exit(1)



def dbg(a):
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    print("type:")
    print(type(a))
    print("data:")
    print(a)

if data.type != nbt2yaml.parse.TAG_Compound or data.name != "":
    print("Error, expected compound nameless root tag", file=sys.stderr)
    sys.exit(1)

file_data = data.data[0]
data_items = file_data.data
for item in data_items:
    if item.name=="Villages":
        _, villages = item.data
        for village in villages:
            this_village = {}
            for datum in village:
                if datum.name in ['CX', 'CY', 'CZ', 'Radius', 'PopSize', 'Golems']:
                    this_village[datum.name] = datum.data
                if datum.name == 'Doors':
                    this_village_doors = []
                    _, doors = datum.data
                    for door in doors:
                        this_door = {}
                        for datum in door:
                            if datum.name in ['X', 'Y', 'Z']:
                                this_door[datum.name] = datum.data
                        this_village_doors.append((this_door['X'], this_door['Y'], this_door['Z']))
                    this_village['Doors'] = this_village_doors
            print(this_village)
