#! /usr/bin/env python3

# Read in .json file with the coordinates of all 420 LEDs.
# Write out C-struct file, with coordinates normalized to sphere
# with radius of 1.0.

import json

coords = json.load(open("../../../led_coords.json"))

SPHERE_RADIUS = 76.0

print("const t_led_coord led_coords[420] = {")
for cnt, c in enumerate(coords):
    x = c[0] / SPHERE_RADIUS
    y = c[1] / SPHERE_RADIUS
    z = c[2] / SPHERE_RADIUS
    if cnt % 21 == 0:
        print("// Triangle: %d" % (cnt // 21))
    if cnt == 419:
        print("    {%.4f, %.4f, %.4f}   // %i" % (x,y,z, cnt))
    else:
        print("    {%.4f, %.4f, %.4f},  // %i" % (x,y,z, cnt))
print("};");

