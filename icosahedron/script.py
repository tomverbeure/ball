# import runpy
# runpy.run_path(path_name='C:\\Users\\tom_v\\projects\\ball\\icosahedron\\script.py') 
# runpy.run_path(path_name='/home/tom/projects/ball/icosahedron/script.py') 

import math
import Part
import Draft
import App
from FreeCAD import Base
import FreeCADGui as Gui
import FreeCAD as App

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

nr_leds_per_side    = 11

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

    rotate_inside_normal = main_triangle_verts[0].cross( main_triangle_verts[2].sub(main_triangle_verts[1]).multiply(0.5).add(main_triangle_verts[1]) )
    rotate_inside   = App.Rotation(rotate_inside_normal, math.degrees(boundary_angle))
    inside_point0 = rotate_inside.multVec(main_triangle_verts[0])

    rotate_inside_normal = main_triangle_verts[1].cross( main_triangle_verts[2].sub(main_triangle_verts[0]).multiply(0.5).add(main_triangle_verts[0]) )
    rotate_inside   = App.Rotation(rotate_inside_normal, math.degrees(boundary_angle))
    inside_point1 = rotate_inside.multVec(main_triangle_verts[1])

    rotate_inside_normal = main_triangle_verts[2].cross( main_triangle_verts[1].sub(main_triangle_verts[0]).multiply(0.5).add(main_triangle_verts[0]) )
    rotate_inside   = App.Rotation(rotate_inside_normal, math.degrees(boundary_angle))
    inside_point2 = rotate_inside.multVec(main_triangle_verts[2])

    outside_step_angle = inside_point0.getAngle(inside_point2) / (nr_leds_per_side-1)
    rotate_side0     = inside_point0.cross(inside_point2)
    rotate_side1     = inside_point1.cross(inside_point2)

    led_locations = []

    for line_nr in range(nr_leds_per_side):

        leds_on_line = nr_leds_per_side - line_nr

        start_point = App.Rotation(rotate_side0, math.degrees(outside_step_angle * line_nr)).multVec(inside_point0)
        end_point   = App.Rotation(rotate_side1, math.degrees(outside_step_angle * line_nr)).multVec(inside_point1)

        if leds_on_line == 1:
            point = start_point
            led_locations.append(point)
            continue

        step_angle    = start_point.getAngle(end_point) / (leds_on_line-1)
        rotate_normal = start_point.cross(end_point)

        for led_nr in range(leds_on_line):
            point = App.Rotation(rotate_normal, math.degrees(step_angle * led_nr)).multVec(start_point)
            led_locations.append(point)

    for led_location in led_locations:
        Draft.makeWire([center, led_location])

