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

doc = App.newDocument()

def p2v(p):

    return Base.Vector(p.X, p.Y, p.Z)

def v2p(v):
    p = Draft.makePoint(v[0], v[1], v[2])

    return p

def cut_plane(part, vecs, invert = False, translate = 0):

    vec1 = vecs[1].sub(vecs[0])
    vec2 = vecs[2].sub(vecs[0])

    if invert:
        plane_normal = vec2.cross(vec1).normalize()
    else:
        plane_normal = vec1.cross(vec2).normalize()

    box_normal  = Base.Vector(0,0,1)

    xy_size     = 1000
    z_size      = 500
    box = Part.makeBox(xy_size, xy_size, z_size)

    loc = Base.Vector(-xy_size/2, -xy_size/2, translate)
    loc = (App.Rotation(box_normal, plane_normal)).multVec(loc)
    loc = loc.add(vecs[0])

    box.Placement.Base     = loc
    box.Placement.Rotation = App.Rotation(box_normal, plane_normal)

    #Part.show(box)

    cut = part.common(box)
    return cut

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

def find_correct_angle(dir_orig, dir_new, desired_angle, angle_epsilon=0.1):

    compensation_angle = 0

    center = Base.Vector(0,0,0)
    v1 = Base.Vector(0, 0, 1)
    v2 = Base.Vector(1, 0, v1.z)
    v3 = Base.Vector(v2.x, 0, 0)

    cnt = 0;

    angle_accuracy = 10

    while cnt < 500:
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

        #Draft.makeWire([vc1, vc2])
        
        vc1_x = Base.Vector(1, vc1.y, vc1.z)
        angle = math.degrees(vc1_x.sub(vc1).getAngle(vc2.sub(vc1)))

        if (angle-desired_angle) > angle_accuracy:
            compensation_angle -= angle_accuracy/4
        elif (angle-desired_angle) < -angle_accuracy:
            compensation_angle += angle_accuracy/4
        elif angle_accuracy > angle_epsilon:
            angle_accuracy = angle_accuracy / 2
        else:
            break

    return compensation_angle

# All units are in mm
triangle_side       = 90
sphere_radius       = triangle_side / 4 * math.sqrt(10 + 2 * math.sqrt(5)) 
penta_radius        = math.sqrt((2 * sphere_radius) ** 2 / 5)
penta_inner_angle   = math.radians(360 / 5)

nr_leds_per_side    = 6

led_max_radius      = 9.4/2
led_conn_radius     = 3.9/2
led_height          = 11
led_conn_length     = 20
led_stickout        = 2

# Distance between the plane of the 3 main vertices and parallel plane towards the center
# that will hold the PCB.
pcb_plane_offset    = 10

if 1:

    center = Base.Vector(0,0,0)
    faces = []

    main_triangle_verts = [
            Base.Vector( -math.cos(penta_inner_angle/2) * penta_radius,  math.sin(penta_inner_angle/2) * penta_radius,  penta_radius/2 ),
            Base.Vector( -math.cos(penta_inner_angle/2) * penta_radius, -math.sin(penta_inner_angle/2) * penta_radius,  penta_radius/2 ),
            #Base.Vector( -math.cos(penta_inner_angle/2) * penta_radius, 0,                                             -penta_radius/2 )
            Base.Vector( -penta_radius, 0,                                             -penta_radius/2 )
            ]
    main_triangle_normal = main_triangle_verts[1].sub(main_triangle_verts[0]).cross(main_triangle_verts[2].sub(main_triangle_verts[0])).normalize()

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

    tetra = Part.makeSolid(shell)
    #Part.show(tetra)

    point0 = Part.makeSphere(5)
    point0.Placement.Base = main_triangle_verts[0];
    Part.show(point0)

    point1 = Part.makeSphere(2.5)
    point1.Placement.Base = main_triangle_verts[1];
    Part.show(point1)


if 1:
    # Create LED locations

    # The angle between 2 triangle points in the plane created with the center
    tetra_side_angle = main_triangle_verts[0].getAngle(main_triangle_verts[1])
    tetra_side_angle_deg = math.degrees(tetra_side_angle)

    boundary_angle = tetra_side_angle / (nr_leds_per_side-1) / 1.5

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
        pass

if 1: 
    # Find intersection of LED ray with PCB plane
    main_triangle_center = Base.Vector( 
            (main_triangle_verts[0][0]+ main_triangle_verts[1][0]+ main_triangle_verts[2][0])/3, 
            (main_triangle_verts[0][1]+ main_triangle_verts[1][1]+ main_triangle_verts[2][1])/3, 
            (main_triangle_verts[0][2]+ main_triangle_verts[1][2]+ main_triangle_verts[2][2])/3)

    scale_factor = (main_triangle_center.Length - pcb_plane_offset) / main_triangle_center.Length

    pcb_triangle_verts = [
        Base.Vector(main_triangle_verts[0]).multiply(scale_factor),
        Base.Vector(main_triangle_verts[1]).multiply(scale_factor),
        Base.Vector(main_triangle_verts[2]).multiply(scale_factor),
    ]

    point0 = Part.makeSphere(5)
    point0.Placement.Base = pcb_triangle_verts[0];
    Part.show(point0)

    point1 = Part.makeSphere(2.5)
    point1.Placement.Base = pcb_triangle_verts[1];
    Part.show(point1)

    pcb_led_intersection = []

    for led_location in led_locations:
        i = line_plane_intersection([led_location, center] , pcb_triangle_verts)
        if None:
            p = Part.makeSphere(1)
            p.Placement.Base = i
            Part.show(p)

        pcb_led_intersection.append(i)

if 1:
    # Create LED holes
    led_holes = []

    cyl_small   = Part.makeBox(1,3, led_conn_length)
    cyl_small.Placement.Base = Base.Vector(-0.5, -1.5, 0)
    #Part.show(cyl_small)

    center_proj = center.sub(Base.Vector(main_triangle_normal).multiply(main_triangle_normal.dot(center.sub(main_triangle_verts[0]))))
    Draft.makeWire([center, center_proj])

    for led_location in led_locations:
        #
        # LED big cylinder
        #
        cyl_big     = Part.makeCylinder(led_max_radius,  led_height)

        angle         = led_location.getAngle(Base.Vector(0,0,1))
        rotate_normal = led_location.cross(Base.Vector(0,0,1))

        # location of the base of the LED
        loc = Base.Vector(0,0,-(led_height-led_stickout))
        loc = (App.Rotation(rotate_normal, math.degrees(-angle))).multVec(loc)
        
        cyl_big.Placement.Base     = led_location.add(loc)
        cyl_big.Placement.Rotation = App.Rotation(rotate_normal, math.degrees(-angle))

        led_holes.append(cyl_big)

        #
        # LED leads hole
        #

        #cyl_small   = Part.makeCylinder(led_conn_radius, led_conn_length)
        cyl_small   = Part.makeBox(1,3, led_conn_length)

        i0 = line_plane_intersection([center, led_location], main_triangle_verts)
        i1 = center_proj
        i2 = Base.Vector(i1.x, i1.y+1, i1.z)
        desired_angle = math.degrees((i0.sub(i1)).getAngle(i2.sub(i1)))
        Draft.makeWire([i1, i0])
        Draft.makeWire([i1, i2])

        compensation_angle = find_correct_angle(Base.Vector(0,0,1), rotate_normal, -desired_angle)

        rotate_z        = App.Rotation(Base.Vector(0,0,1), compensation_angle)
        rotate_ray      = App.Rotation(rotate_normal, math.degrees(-angle))
        rotate_final    = rotate_ray.multiply(rotate_z)

        #loc = Base.Vector(0,0,-(led_height-led_stickout)-led_conn_length)
        loc = Base.Vector(-0.5,-1.5,-(led_height-led_stickout)-led_conn_length)
        loc = rotate_final.multVec(loc)


        cyl_small.Placement.Base     = led_location.add(loc)
        cyl_small.Placement.Rotation = rotate_final

        led_holes.append(cyl_small)

        #Part.show(cyl_big)
        #Part.show(cyl_small)

if 1:
    # Create sphere segment

    sphere = Part.makeSphere(sphere_radius)
    #sphere = sphere.cut(Part.makeSphere(sphere_radius-15))

if 1:
    # Cut LED holes
    for led_hole in led_holes:
        sphere = sphere.cut(led_hole)

if 1:
    # Cut sphere into rounded tetra
    sphere = cut_plane(sphere, [center, main_triangle_verts[0], main_triangle_verts[2]])
    sphere = cut_plane(sphere, [center, main_triangle_verts[2], main_triangle_verts[1]])
    sphere = cut_plane(sphere, [center, main_triangle_verts[1], main_triangle_verts[0]])
    #sphere = cut_plane(sphere, main_triangle_verts, invert = True, translate = -pcb_plane_offset)
    sphere = cut_plane(sphere, main_triangle_verts, invert = True, translate = -10)
    Part.show(sphere)


App.ActiveDocument.recompute()

