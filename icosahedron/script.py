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
import PySide

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

def find_correct_angle(dir_orig, dir_new, desired_angle, angle_epsilon=0.01, search_dir = 1):
    App.Console.PrintMessage("\nfind_correct_angle\n")
    App.Console.PrintMessage("dir_orig:")
    App.Console.PrintMessage(dir_orig)
    App.Console.PrintMessage("\n")
    App.Console.PrintMessage("dir_new:")
    App.Console.PrintMessage(dir_new)
    App.Console.PrintMessage("\n")
    App.Console.PrintMessage("desired_angle:")
    App.Console.PrintMessage(desired_angle)
    App.Console.PrintMessage("\n")

#    desired_angle = (desired_angle + 360) % 360
#
#    App.Console.PrintMessage("desired_angle:")
#    App.Console.PrintMessage(desired_angle)
#    App.Console.PrintMessage("\n")

    compensation_angle = 0

    center = Base.Vector(0,0,0)
    v1 = Base.Vector(0, 0, 1)       # Z-axis corner
    v2 = Base.Vector(0, 1, 1)       # Y-shifted Z-axis corner
    v3 = Base.Vector(0, 1, 0)       # Y-shifted center corner

    cnt = 0;

    angle_accuracy = 30

    while cnt < 20:
        App.Console.PrintMessage(".")
        cnt = cnt + 1

        dir_rot     = App.Rotation(dir_orig, dir_new).multiply(App.Rotation(dir_orig, compensation_angle))
        
        vr1 = dir_rot.multVec(v1)
        vr2 = dir_rot.multVec(v2)
        vr3 = dir_rot.multVec(v3)
        
        x_plane_coord = 1 
        x_plane = [ 
                Base.Vector(x_plane_coord, 0, 0),
                Base.Vector(x_plane_coord, 1, 0),
                Base.Vector(x_plane_coord, 0, 1)
                ]


        # Intersection between rotated Z-axis line and X-plane
        vc1 = line_plane_intersection(
            [ center, vr1], 
            x_plane
            )

        if vc1 is None:
            App.Console.PrintMessage("\n================================\n")
            Draft.makeWire([x_plane[0], x_plane[1]])
            Draft.makeWire([x_plane[0], x_plane[2]])
            App.Console.PrintMessage("x_plane:")
            App.Console.PrintMessage(x_plane)
            App.Console.PrintMessage("\n")
            App.Console.PrintMessage("vr1:")
            App.Console.PrintMessage(vr1)
            App.Console.PrintMessage("\n")
            App.Console.PrintMessage("vc1:")
            App.Console.PrintMessage(vc1)
            App.Console.PrintMessage("\n")
            App.ActiveDocument.recompute()
            raise Exception("Aborted...")
        
        # Intersection between rotated Y-shifted Z-axis line and X-plane
        vc2 = line_plane_intersection(
            [ vr3, vr2 ], 
            x_plane
            )

        angle  = math.degrees( Base.Vector(0,1,0).getAngle(Base.Vector(vc2.sub(vc1))) )

        #App.Console.PrintMessage("angle:")
        #App.Console.PrintMessage(angle)
        #App.Console.PrintMessage("\n")

        delta_angle = angle-desired_angle

        #App.Console.PrintMessage("delta_angle:")
        #App.Console.PrintMessage(delta_angle)
        #App.Console.PrintMessage("\n")

        if (angle-desired_angle) > angle_accuracy:
            compensation_angle = compensation_angle - search_dir * angle_accuracy/4
        elif (angle-desired_angle) < -angle_accuracy:
            compensation_angle = compensation_angle + search_dir * angle_accuracy/4
        elif angle_accuracy > angle_epsilon:
            angle_accuracy = angle_accuracy / 2
        else:
            break

        #App.Console.PrintMessage("compensation_angle:")
        #App.Console.PrintMessage(compensation_angle)
        #App.Console.PrintMessage("\n")

        #Draft.makeWire([vc1, vc2])

    App.Console.PrintMessage("compensation_angle:")
    App.Console.PrintMessage(compensation_angle)
    App.Console.PrintMessage("\n")

    #Draft.makeWire([vc1, vc2])

    return compensation_angle

def create_tetra(verts):
    # Create tetrahedron from 3 main verticesa and the center vertex
    faces = []

    center = Base.Vector(0,0,0)

    # Main triangle
    polygon     = Part.makePolygon([ verts[0], verts[1], verts[2], verts[0] ])
    faces.append(Part.Face(polygon))

    # Top triangle
    polygon     = Part.makePolygon([ verts[0], verts[1], center, verts[0] ])
    faces.append(Part.Face(polygon))

    # Side triangle 1
    polygon     = Part.makePolygon([ verts[0], verts[2], center, verts[0] ])
    faces.append(Part.Face(polygon))

    # Side triangle 2
    polygon     = Part.makePolygon([ verts[1], verts[2], center, verts[1] ])
    faces.append(Part.Face(polygon))

    shell = Part.makeShell(faces)
    tetra = Part.makeSolid(shell)

    return tetra

def create_triangle_vertices(penta_radius):
    #============================================================
    # Create the triangle vertices
    #============================================================

    
    # Initially, the vertices are the canonical ones where the plane of the triangle is not aligned with a X plane.
    main_triangle_verts = [
            Base.Vector( -math.cos(penta_inner_angle/2) * penta_radius,  math.sin(penta_inner_angle/2) * penta_radius,  penta_radius/2 ),
            Base.Vector( -math.cos(penta_inner_angle/2) * penta_radius, -math.sin(penta_inner_angle/2) * penta_radius,  penta_radius/2 ),
            Base.Vector( -penta_radius, 0,                                                                             -penta_radius/2 )
            ]
    main_triangle_normal = main_triangle_verts[1].sub(main_triangle_verts[0]).cross(main_triangle_verts[2].sub(main_triangle_verts[0])).normalize()

    # Orthogonal projects of center onto the triangle plane, then rotate this center to coincide with the X axis.
    center_proj = center.sub(Base.Vector(main_triangle_normal).multiply(main_triangle_normal.dot(center.sub(main_triangle_verts[0]))))
    rotate_main_verts = App.Rotation(center_proj, Base.Vector(-1, 0, 0))

    # Rotate the triangle vertices just the same.
    new_verts = []
    for vert in main_triangle_verts:
        new_verts.append(rotate_main_verts.multVec(vert))

    # The triangle vertices now form a plan that is parallel to the YZ plane and perpendicular to the X axis.
    # This is just easier to deal with later...
    main_triangle_verts = new_verts
    main_triangle_normal = main_triangle_verts[1].sub(main_triangle_verts[0]).cross(main_triangle_verts[2].sub(main_triangle_verts[0])).normalize()

    return main_triangle_verts

def create_led_locations(triangle_verts, nr_leds_per_side):
    #============================================================
    # Create LED locations
    #============================================================

    # The angle between 2 triangle points in the plane created with the center
    tetra_side_angle = triangle_verts[0].getAngle(triangle_verts[1])

    boundary_angle = tetra_side_angle / (nr_leds_per_side-1) / 1.5

    rotate_inside_normal = triangle_verts[0].cross( triangle_verts[2].sub(triangle_verts[1]).multiply(0.5).add(triangle_verts[1]) )
    rotate_inside   = App.Rotation(rotate_inside_normal, math.degrees(boundary_angle))
    inside_point0 = rotate_inside.multVec(triangle_verts[0])

    rotate_inside_normal = triangle_verts[1].cross( triangle_verts[2].sub(triangle_verts[0]).multiply(0.5).add(triangle_verts[0]) )
    rotate_inside   = App.Rotation(rotate_inside_normal, math.degrees(boundary_angle))
    inside_point1 = rotate_inside.multVec(triangle_verts[1])

    rotate_inside_normal = triangle_verts[2].cross( triangle_verts[1].sub(triangle_verts[0]).multiply(0.5).add(triangle_verts[0]) )
    rotate_inside   = App.Rotation(rotate_inside_normal, math.degrees(boundary_angle))
    inside_point2 = rotate_inside.multVec(triangle_verts[2])

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
        #Draft.makeWire([center, led_location])
        pass

    return led_locations

# All units are in mm
triangle_side       = 90
sphere_radius       = triangle_side / 4 * math.sqrt(10 + 2 * math.sqrt(5)) 
penta_radius        = math.sqrt((2 * sphere_radius) ** 2 / 5)
penta_inner_angle   = math.radians(360 / 5)

nr_leds_per_side    = 6

led_max_radius      = 9.4/2                 # Max radius of bulb at the bottom
led_height          = 11                    # Height of the bulb
led_conn_width      = 3.9                   # Joint width of the 4 LED connectors
led_stickout        = 2                     # How high the LED sticks out from the sphere

led_conn_length     = 25.4-1.6              # Minimum length of the LED connectors (See WS2812D-F8 datasheet)
led_shaft_width     = led_conn_width + 1    # Width of the LED connector shaft
led_shaft_height    = 2                     # Height of the LED connector shaft

# Distance between the plane of the 3 main vertices and parallel plane towards the center
# that will hold the PCB.
pcb_plane_offset    = 10

center              = Base.Vector(0,0,0)

main_triangle_verts     = create_triangle_vertices(penta_radius)
main_triangle_normal    = main_triangle_verts[1].sub(main_triangle_verts[0]).cross(main_triangle_verts[2].sub(main_triangle_verts[0])).normalize()
led_locations           = create_led_locations(main_triangle_verts, nr_leds_per_side)

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

    if 1:
        point0 = Part.makeSphere(5)
        point0.Placement.Base = pcb_triangle_verts[0];
        Part.show(point0)
    
        point1 = Part.makeSphere(2.5)
        point1.Placement.Base = pcb_triangle_verts[1];
        Part.show(point1)

    pcb_led_intersection = []

    for led_location in led_locations:
        i = line_plane_intersection([led_location, center] , pcb_triangle_verts)
        pcb_led_intersection.append(i)

        if None:
            p = Part.makeSphere(1)
            p.Placement.Base = i
            Part.show(p)

if 1:
    # Create LED holes
    led_holes = []

    led_shaft   = Part.makeBox(led_shaft_height ,led_shaft_width, led_conn_length)
    led_shaft.Placement.Base = Base.Vector(-led_shaft_height/2, -led_shaft_width/2, 0)
    #Part.show(led_shaft)

    center_proj = center.sub(Base.Vector(main_triangle_normal).multiply(main_triangle_normal.dot(center.sub(main_triangle_verts[0]))))
    Draft.makeWire([center, center_proj])

    for led_location in led_locations:
    #led_location = led_locations[14]
    #if True:
        rotate_led = App.Rotation(Base.Vector(0,0,1),led_location)

        #
        # LED big cylinder
        #
        cyl_big     = Part.makeCylinder(led_max_radius,  led_height)

        # location of the base of the LED
        loc = Base.Vector(0,0,-(led_height-led_stickout))
        loc = rotate_led.multVec(loc)
        
        cyl_big.Placement.Base     = led_location.add(loc)
        cyl_big.Placement.Rotation = rotate_led

        led_holes.append(cyl_big)

        #
        # LED shaft 
        #

        led_shaft   = Part.makeBox(led_shaft_height,led_shaft_width, led_conn_length)

        i0 = line_plane_intersection([center, led_location], main_triangle_verts)
        i1 = center_proj
        i2 = Base.Vector(i1.x, i1.y+1, i1.z)
        angle_to_center = math.degrees((i0.sub(i1)).getAngle(i2.sub(i1)))
        App.Console.PrintMessage("angle_to_center:")
        App.Console.PrintMessage(angle_to_center)
        App.Console.PrintMessage("\n")
        App.Console.PrintMessage("i0:")
        App.Console.PrintMessage(i0)
        App.Console.PrintMessage("\n")

        if i0.y >= 0 and i0.z >= 0:
            desired_angle = 90-angle_to_center
            angle_sign    = 1
        elif i0.y < 0 and i0.z >= 0:
            desired_angle = angle_to_center-90
            angle_sign    = -1
        elif i0.y >= 0 and i0.z < 0:
            desired_angle = 90-angle_to_center
            angle_sign    = -1
        elif i0.y < 0 and i0.z < 0:
            desired_angle = angle_to_center-90
            angle_sign    = 1
        else:
            desired_angle = 0

        #Draft.makeWire([i1, i0])
        #Draft.makeWire([i1, i2])

        compensation_angle = find_correct_angle(Base.Vector(0,0,1), led_location, desired_angle, search_dir = angle_sign)

        rotate_z        = App.Rotation(Base.Vector(0,0,1), compensation_angle)
        rotate_final    = rotate_led.multiply(rotate_z)

        loc = Base.Vector(-led_shaft_height/2,-led_shaft_width/2,-(led_height-led_stickout)-led_conn_length)
        loc = rotate_final.multVec(loc)


        led_shaft.Placement.Base     = led_location.add(loc)
        led_shaft.Placement.Rotation = rotate_final

        led_holes.append(led_shaft)

        Part.show(cyl_big)
        Part.show(led_shaft)

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
Gui.activeDocument().activeView().viewRight()
Gui.SendMsgToActiveView("ViewFit")

