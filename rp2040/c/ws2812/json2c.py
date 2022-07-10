#! /usr/bin/env python3

# Read in .json file with the coordinates of all 420 LEDs.
# Write out C-struct file, with coordinates normalized to sphere
# with radius of 1.0.

import json
import sys
from operator import itemgetter

coords = json.load(open("../../../led_coords.json"))

SPHERE_RADIUS = 76.0

if True:
    print("const t_led_coord led_coords[420] = {")
    for cnt, c in enumerate(coords):
        x = c[0] / SPHERE_RADIUS
        y = c[1] / SPHERE_RADIUS
        z = c[2] / SPHERE_RADIUS
        if cnt % 21 == 0:
            print("    // Triangle: %d" % (cnt // 21))
        if cnt == 419:
            print("    {%.4f, %.4f, %.4f}   // %i" % (x,y,z, cnt))
        else:
            print("    {%.4f, %.4f, %.4f},  // %i" % (x,y,z, cnt))
    print("};");


if True:
    closest_points_list = []

    for cur_cnt, cur_c in enumerate(coords):

        distances = []

        for cl_cnt, cl_c in enumerate(coords):
            if cur_cnt == cl_cnt:
                continue

            dist = (cur_c[0]-cl_c[0])**2 + (cur_c[1]-cl_c[1])**2 + (cur_c[2]-cl_c[2])**2  
            distances.append([cl_cnt, dist])

        sorted_distances = sorted(distances, key=lambda x:x[1])

        closest_points = []
        for i in range(0,6):
            closest_points.append(sorted_distances[i][0])

        closest_points_list.append(closest_points)

    print()
    print("const uint16_t closest_leds[420][6] = {");
    for cnt in range(0,420):
        if cnt % 21 == 0:
            print("    // Triangle: %d" % (cnt // 21))
        print("    { ", end="")
        print(*closest_points_list[cnt], sep=", ", end="")
        print("}", end="")
        if cnt != 419:
            print(",")
        else:
            print("")
    print("};")
    
    
