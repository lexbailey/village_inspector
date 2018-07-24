#!/usr/bin/env python

from __future__ import print_function
import argparse
import subprocess
import sys
import nbt2yaml
import svgwrite

p = argparse.ArgumentParser()
p.add_argument("villagefile")
p.add_argument("outputdir")
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

def min_coords(coords_list):
    minimal = [None, None, None]
    for i in range(len(minimal)):
        minimal[i] = min([coords[i] for coords in coords_list])
    return tuple(minimal)

def vect_add(a, b):
    return tuple([sum(ab) for ab in zip(a,b)])

def vect_mul(a, b):
    return tuple([ai * bi for ai, bi in zip(a,b)])

def vect_sub(a, b):
    return tuple([ai - bi for ai, bi in zip(a,b)])

def normalise_coords(coords_list, origin):
    if type(coords_list) == list:
        return [
            vect_sub(coords, origin)
            for coords in coords_list
        ]
    else:
        return vect_sub(coords_list, origin)

def xyz_to_xz(xyz):
    return xyz[0], xyz[2]
    
def box_origin(size, point):
    point_xy = xyz_to_xz(point)
    topleft = vect_mul(point_xy, size)
    return topleft

def box_centre(size, point):
    return vect_add(box_origin(size, point), vect_mul(point, (0.5,0.5,0.5)))

def draw_village(village, dwg, group):
    square_size = (20,20)
    origin = min_coords(village['Doors'])
    doors = normalise_coords(village['Doors'], origin)
    centre = normalise_coords(village['centre'], origin)
    c = box_centre(square_size, centre)
    group.add(dwg.circle(c, r=20 * village['Radius'], fill='rgb(64,64,255)', fill_opacity=100, stroke='white'))
    for door in doors:
        topleft = box_origin(square_size, door)
        group.add(dwg.rect(topleft, square_size, fill='rgb(85, 34, 0)', stroke='white'))
    group.add(dwg.circle(c, r=10, fill='blue', stroke='white'))
    group.add(dwg.text("%d, %d" % xyz_to_xz(village['centre']), c, font_size=40))

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
            this_village['centre'] = (this_village['CX'], this_village['CY'], this_village['CZ'])
            print(this_village)
            drawing = svgwrite.Drawing("%s/%s" % (args.outputdir, "%d_%d_%d" % this_village['centre']), size=(500, 500))
            villagegroup = svgwrite.container.Group(transform='scale(0.5,0.5)')
            drawing.add(villagegroup)
            draw_village(this_village, drawing, villagegroup)
            drawing.add(drawing.text("Doors: %d" % len(this_village['Doors']), (20,400), font_size=20))
            drawing.add(drawing.text("Villagers: %d" % this_village['PopSize'], (20,430), font_size=20))
            drawing.add(drawing.text("Golems: %d" % this_village['Golems'], (20,460), font_size=20))
            drawing.save()
