
# runpy.run_path(path_name='/home/tom/projects/ball/icosahedron/test.py') 

import math
import Part
import Draft
import App
from FreeCAD import Base
import FreeCADGui as Gui
import FreeCAD as App

def s(v,r):
    sf = Part.makeSphere(r)
    sf.Placement.Base = v
    Part.show(sf)

def line_plane_intersection(line, plane):
    # https://stackoverflow.com/questions/5666222/3d-line-plane-intersection

    # line = 2 vectors (coordinates)
    # plane = 3 vectors (coordinates)
    
    line_dir = line[1].sub(line[0])
    plane_normal = plane[1].sub(plane[0]).cross(plane[2].sub(plane[0]))

    dot = line_dir.dot(plane_normal)

    if abs(dot) > 1e-6:
        w = line[0].sub(plane[0])
        fac = -plane_normal.dot(w) / dot
        u = Base.Vector(line_dir).multiply(fac)
        r = line[0].add(u)
        return r

    return None

def find_correct_angle(dir_orig, dir_new, desired_angle):

    compensation_angle = 0

    center = Base.Vector(0,0,0)
    v1 = Base.Vector(0, 0, 1)
    v2 = Base.Vector(1, 0, v1.z)
    v3 = Base.Vector(v2.x, 0, 0)

    cnt = 0;

    while cnt < 1440:
        cnt = cnt + 1

        dir_rot     = App.Rotation(dir_orig, dir_new).multiply(App.Rotation(dir_orig, compensation_angle))
        
        vr1 = dir_rot.multVec(v1)
        vr2 = dir_rot.multVec(v2)
        vr3 = dir_rot.multVec(v3)
        
        y_plane_coord = 1 
        y_plane = [ 
                Base.Vector(0, y_plane_coord, 0),
                Base.Vector(1, y_plane_coord, 0),
                Base.Vector(0, y_plane_coord, 1)
                ]
        
        vc1 = line_plane_intersection(
            [ vr1, center], 
            y_plane
            )
        
        vc2 = line_plane_intersection(
            [ vr2, vr3], 
            y_plane
            )

        Draft.makeWire([vc1, vc2])
        
        vc1_x = Base.Vector(1, vc1.y, vc1.z)
        angle = math.degrees(vc1_x.sub(vc1).getAngle(vc2.sub(vc1)))

        if (angle-desired_angle) > 0.05:
            compensation_angle -= 0.025
        elif (angle-desired_angle) < -0.05:
            compensation_angle += 0.025
        else:
            break

    s(vc1, 0.02)
    s(vc2, 0.02)

    return compensation_angle


doc = App.newDocument()


center = Base.Vector(0,0,0)

dir_orig = Base.Vector(0,0,1)
dir_new  = Base.Vector(1,2,3)
dir_rot  = App.Rotation(dir_orig, dir_new)

m = Base.Matrix()
m = dir_rot

v1 = Base.Vector(0, 0, 0.5)
v2 = Base.Vector(0.2, 0, v1.z)
v3 = Base.Vector(v2.x, 0, 0)

b_orig = Part.makeBox(v2.x, 0.05, v2.z)
Part.show(b_orig)

b_rot = Part.makeBox(v2.x, 0.05, v2.z)
b_rot.Placement.Rotation = dir_rot
Part.show(b_rot)

vr1 = dir_rot.multVec(v1)
vr2 = dir_rot.multVec(v2)
vr3 = dir_rot.multVec(v3)

s(vr1, 0.02)
s(vr2, 0.02)
s(vr3, 0.02)

y_plane_coord = 0.2
y_plane = [ 
        Base.Vector(0, y_plane_coord, 0),
        Base.Vector(1, y_plane_coord, 0),
        Base.Vector(0, y_plane_coord, 1)
        ]

vc1 = line_plane_intersection(
    [ vr1, center], 
    y_plane
    )

vc2 = line_plane_intersection(
    [ vr2, vr3], 
    y_plane
    )

s(vc1, 0.02)
s(vc2, 0.02)

vc1_x = Base.Vector(0.2, vc1.y, vc1.z)

s(vc1_x, 0.02)

angle = find_correct_angle(dir_orig, dir_new, 0)

b_final = Part.makeBox(v2.x, 0.05, v2.z)
b_final.Placement.Rotation = dir_rot.multiply(App.Rotation(dir_orig, angle))
Part.show(b_final)

enclosure = Part.makeBox(1,0.2,10)
enclosure.Placement.Base = Base.Vector(0,0,-5)
cut = enclosure.common(b_final)
Part.show(cut)

App.ActiveDocument.recompute()
