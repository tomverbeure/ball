#!/usr/bin/env python3

from solid import *
from solid.utils import *

icosahedron = import_scad('Icosahedron.scad')

trunc_ico = import_scad('TruncatedGreatIcosahedron-solid.scad')

#ball = icosahedron.icosahedron(5)
ball = trunc_ico.show_solid

d = difference()(
    cube(12),
    sphere(15)
)

def equilat_tr():
    t = polygon([ [0,0], [1,0], [math.cos(60/180*math.pi), math.sin(60/180*math.pi)] ])

    mid_x = (math.cos(60/180*math.pi) + 1) / 3
    mid_y = (math.sin(60/180*math.pi)) / 3

    hole0 = translate([0,0,-1])(cylinder(r=0.05, h=2, segments=20))
    hole1 = translate([mid_x,mid_y,-1])(cylinder(r=0.05, h=2, segments=20))


    return t-hole0-hole1

def hexagon():
    t0 = equilat_tr()
    t1 = rotate(a=60, v=UP_VEC)(equilat_tr()) 
    t2 = rotate(a=120, v=UP_VEC)(equilat_tr()) 
    t3 = rotate(a=180, v=UP_VEC)(equilat_tr()) 
    t4 = rotate(a=240, v=UP_VEC)(equilat_tr()) 
    t5 = rotate(a=300, v=UP_VEC)(equilat_tr()) 

    h=t0+t1+t2+t3+t4+t5
    #h=t0

    return h

scene = hexagon()

print(scad_render(scene))


