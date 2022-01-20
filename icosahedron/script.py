# import runpy
# runpy.run_path(path_name='C:\\Users\\tom_v\\projects\\ball\\icosahedron\\script.py') 
# runpy.run_path(path_name='/home/tom/projects/ball/icosahedron/script.py') 

import math
import Part
import Draft
from FreeCAD import Base
import FreeCADGui as Gui

def p2v(p):

    return Base.Vector(p.X, p.Y, p.Z)

def v2p(v):
    p = Draft.makePoint(v[0], v[1], v[2])

    return p

if None:
    vec1 = Base.Vector(0, 0, 0)
    vec2 = Base.Vector(10, 0, 0)
    line = Part.LineSegment(vec1, vec2)
    edge = line.toShape()
    Part.show(edge)
    pass


# All units are in mm
triangle_side       = 50
sphere_radius       = triangle_side / 4 * math.sqrt(10 + 2 * math.sqrt(5)) 
penta_radius        = math.sqrt((2 * sphere_radius) ** 2 / 5)
penta_inner_angle   = math.radians(360 / 5)

nr_leds_per_side    = 7

if 1:

    center = Base.Vector(0,0,0)
    faces = []

    main_triangle_verts = [
            Base.Vector( -math.cos(penta_inner_angle/2) * penta_radius,  math.sin(penta_inner_angle/2) * penta_radius,  penta_radius/2 ),
            Base.Vector( -math.cos(penta_inner_angle/2) * penta_radius, -math.sin(penta_inner_angle/2) * penta_radius,  penta_radius/2 ),
            #Base.Vector( -math.cos(penta_inner_angle/2) * penta_radius, 0,                                             -penta_radius/2 )
            Base.Vector( -penta_radius, 0,                                             -penta_radius/2 )
            ]

    # Main triangle
    polygon     = Part.makePolygon([ main_triangle_verts[0], main_triangle_verts[1], main_triangle_verts[2], main_triangle_verts[0] ])
    faces.append(Part.Face(polygon))

    # Top triangle
    polygon     = Part.makePolygon([ main_triangle_verts[0], main_triangle_verts[1], center, main_triangle_verts[0] ])
    faces.append(Part.Face(polygon))

    # Side triangle 1
    polygon     = Part.makePolygon([ main_triangle_verts[0], main_triangle_verts[2], center, main_triangle_verts[0] ])
    faces.append(Part.Face(polygon))

    # Side triangle 2
    polygon     = Part.makePolygon([ main_triangle_verts[1], main_triangle_verts[2], center, main_triangle_verts[1] ])
    faces.append(Part.Face(polygon))

    shell = Part.makeShell(faces)
    solid = Part.makeSolid(shell)

    Part.show(solid)

if 1:
    # Create LED locations

    # The angle between 2 triangle points in the plane created with the center
    tetra_side_angle = main_triangle_verts[0].getAngle(main_triangle_verts[1])
    tetra_side_angle_deg = math.degrees(tetra_side_angle)

    boundary_angle = tetra_side_angle / (nr_leds_per_side + 1) / 2
#    led_angle = tetra_side_angle / (nr_leds_per_side+1)

    #inside_point0   = Draft.makePoint(main_triangle_verts[0][0], main_triangle_verts[0][1], main_triangle_verts[0][2])
    inside_point0   = v2p(main_triangle_verts[0])
    rotate_inside   = main_triangle_verts[0].cross( main_triangle_verts[2].sub(main_triangle_verts[1]).multiply(0.5).add(main_triangle_verts[1]) )
    Draft.rotate(inside_point0, math.degrees(boundary_angle), center=center, axis = rotate_inside, copy=False)
    Draft.makeWire([center, p2v(inside_point0)])

    inside_point1   = v2p(main_triangle_verts[1])
    rotate_inside   = main_triangle_verts[1].cross( main_triangle_verts[2].sub(main_triangle_verts[0]).multiply(0.5).add(main_triangle_verts[0]) )
    Draft.rotate(inside_point1, math.degrees(boundary_angle), center=center, axis = rotate_inside, copy=False)
    Draft.makeWire([center, p2v(inside_point1)])

    inside_point2   = v2p(main_triangle_verts[2])
    rotate_inside   = main_triangle_verts[2].cross( main_triangle_verts[1].sub(main_triangle_verts[0]).multiply(0.5).add(main_triangle_verts[0]) )
    Draft.rotate(inside_point2, math.degrees(boundary_angle), center=center, axis = rotate_inside, copy=False)
    Draft.makeWire([center, p2v(inside_point2)])

    outside_step_angle = p2v(inside_point0).getAngle(p2v(inside_point2)) / nr_leds_per_side
    rotate_side0     = p2v(inside_point0).cross(p2v(inside_point2))
    rotate_side1     = p2v(inside_point1).cross(p2v(inside_point2))

    for line_nr in range(nr_leds_per_side):

        leds_on_line = nr_leds_per_side - line_nr

        start_point = Draft.rotate(inside_point0, math.degrees(outside_step_angle * line_nr), center=center, axis=rotate_side0, copy=True)
        end_point   = Draft.rotate(inside_point1, math.degrees(outside_step_angle * line_nr), center=center, axis=rotate_side1, copy=True)

#        for h in range(v):
#            rotation_normal = p2v(inside_point0).cross(p2v(inside_point1))
#            angle = p2v(inside_point0).getAngle(p2v(inside_point1)) / v

            #Draft.rotate(inside_point0, math.degrees(angle * h), center=center, axis=rotation_normal, copy=True)

#    rotation_normal_side0 = (main_triangle_verts[0].cross(main_triangle_verts[2])).normalize()
#    rotation_normal_side1 = (main_triangle_verts[1].cross(main_triangle_verts[2])).normalize()
#
#    start_point = Draft.makePoint(main_triangle_verts[0][0], main_triangle_verts[0][1], main_triangle_verts[0][2])
#    end_point   = Draft.makePoint(main_triangle_verts[1][0], main_triangle_verts[1][1], main_triangle_verts[1][2])
#
#    Draft.rotate(start_point, math.degrees(boundary_angle), center=center, axis = rotation_normal_side0, copy=False)
#    Draft.rotate(end_point,   math.degrees(boundary_angle), center=center, axis = rotation_normal_side1, copy=False)
#
#    Draft.makeWire([center, p2v(start_point)])
#    Draft.makeWire([center, p2v(end_point)])
#
#    Draft.makeWire([center, main_triangle_verts[0]])

#    point0 = Draft.rotate(start_point, math.degrees(led_angle/2), center=center, axis= rotation_normal, copy=True)
#    for i in range(nr_leds_per_side+1):
#        point = Draft.rotate(point0, math.degrees(led_angle * i), center=center, axis= rotation_normal, copy=True)
#
#    start_point = Draft.rotate(start_point, math.degree

        

