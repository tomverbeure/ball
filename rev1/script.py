# import runpy
# runpy.run_path(path_name='C:\\Users\\tom_v\\projects\\ball\\rev1\\script.py') 
# runpy.run_path(path_name='C:\\Users\\tverbeure\\projects\\ball\\rev1\\script.py') 
# runpy.run_path(path_name='/home/tom/projects/ball/rev1/script.py') 
# runpy.run_path(path_name='/Users/tverbeure/projects/ball/rev1/script.py')
# runpy.run_path(path_name='/Users/tom/projects/ball/rev1/script.py')

import math
import Part
import Draft
from FreeCAD import Base
import FreeCADGui as Gui
import FreeCAD as App
import PySide

doc = App.newDocument()

#============================================================
# Adjustable parameters
#============================================================

# All units are in mm
triangle_side       = 80
sphere_radius       = triangle_side / 4 * math.sqrt(10 + 2 * math.sqrt(5)) 
penta_radius        = math.sqrt((2 * sphere_radius) ** 2 / 5)
penta_inner_angle   = math.radians(360 / 5)

nr_leds_per_side    = 6

led_max_radius      = 10.4/2                # Max radius of bulb at the bottom
led_height          = 11                    # Height of the bulb
led_conn_width      = 3.9                   # Joint width of the 4 LED connectors
led_stickout        = 2                     # How high the LED sticks out from the sphere

led_conn_length     = 25.4-1.6              # Minimum length of the LED connectors (See WS2812D-F8 datasheet)
led_shaft_width     = led_conn_width + 1.5  # Width of the LED connector shaft
led_shaft_height    = 2.5                   # Height of the LED connector shaft

# Alignment boxes on the side
align_box_size_x        = 3.5
align_box_size_y        = 10
align_box_size_z        = 1

# Distance between the plane of the 3 main vertices and parallel plane towards the center
# that will hold the PCB.
pcb_plane_offset    = 6
pcb_thickness       = 1.6

# screw inserts for M2 screws
#screw_insert_radius = 1.6
#screw_insert_radius = 0.8
#screw_insert_height = 5 

# Dimensions for a magnet with radius 4 and depth 4
screw_insert_radius = (4 + 1.2)/2
screw_insert_height = 4 + 1

pcb_hole_radius     = 8.4/2                     # M2 screw

# These are the side magnets that keep triangles together.
magnet_radius           = (5 + 0.6) / 2            # + 0.6 for margin.
magnet_height           = 1.7 + 0.3
magnet_dist_from_shell  = 1

pcb_gap_length      = 20 
pcb_gap_width       = 3.5 

inner_foot_radius       = pcb_hole_radius - 0.4

# Gap between PCB gap and inner support
inner_pcb_gap_margin    = 0.5
inner_pcb_clearance     = 3

#============================================================

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
#    App.Console.PrintMessage("\nfind_correct_angle\n")
#    App.Console.PrintMessage("dir_orig:")
#    App.Console.PrintMessage(dir_orig)
#    App.Console.PrintMessage("\n")
#    App.Console.PrintMessage("dir_new:")
#    App.Console.PrintMessage(dir_new)
#    App.Console.PrintMessage("\n")
#    App.Console.PrintMessage("desired_angle:")
#    App.Console.PrintMessage(desired_angle)
#    App.Console.PrintMessage("\n")

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
#        App.Console.PrintMessage(".")
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

#    App.Console.PrintMessage("compensation_angle:")
#    App.Console.PrintMessage(compensation_angle)
#    App.Console.PrintMessage("\n")

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
    rotate_main_verts     = App.Rotation(center_proj, Base.Vector(-1, 0, 0))
    rev_rotate_main_verts = App.Rotation(Base.Vector(-1, 0, 0), center_proj)

    # Rotate the triangle vertices just the same.
    new_verts = []
    for vert in main_triangle_verts:
        new_verts.append(rotate_main_verts.multVec(vert))

    # The triangle vertices now form a plane that is parallel to the YZ plane and perpendicular to the X axis.
    # This is just easier to deal with later...
    main_triangle_verts = new_verts
    main_triangle_normal = main_triangle_verts[1].sub(main_triangle_verts[0]).cross(main_triangle_verts[2].sub(main_triangle_verts[0])).normalize()

    return [ main_triangle_verts, main_triangle_normal, rotate_main_verts, rev_rotate_main_verts ]

def create_led_locations(triangle_verts, nr_leds_per_side):
    #============================================================
    # Create LED locations
    #============================================================

    # The angle between 2 triangle points in the plane created with the center
    tetra_side_angle = triangle_verts[0].getAngle(triangle_verts[1])

    # 1.3 is a magic number. This number should be calculated because a different
    # number is needed for different number of LEDs.
    boundary_angle = tetra_side_angle / (nr_leds_per_side-1) / 1.5

    # Calculate the location of 3 LEDs in the corner.
    # The corner LEDs are placed along the curve from a triangle corner to the middle 
    # of the line between the 2 corners on the other side.

    # t0 x ( 1/2 * (t2 - t1) ) + t1 )
    rotate_inside_normal = triangle_verts[0].cross( triangle_verts[2].sub(triangle_verts[1]).multiply(0.5).add(triangle_verts[1]) )
    rotate_inside   = App.Rotation(rotate_inside_normal, math.degrees(boundary_angle))
    inside_point0 = rotate_inside.multVec(triangle_verts[0])

    rotate_inside_normal = triangle_verts[1].cross( triangle_verts[2].sub(triangle_verts[0]).multiply(0.5).add(triangle_verts[0]) )
    rotate_inside   = App.Rotation(rotate_inside_normal, math.degrees(boundary_angle))
    inside_point1 = rotate_inside.multVec(triangle_verts[1])

    rotate_inside_normal = triangle_verts[2].cross( triangle_verts[1].sub(triangle_verts[0]).multiply(0.5).add(triangle_verts[0]) )
    rotate_inside   = App.Rotation(rotate_inside_normal, math.degrees(boundary_angle))
    inside_point2 = rotate_inside.multVec(triangle_verts[2])

    # Calculate the rotation matrix to go from one LED location to the next, along 2
    # axes.
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

    if 0:
        for led_location in led_locations:
            Draft.makeWire([center, led_location])
            pass

    return led_locations


center              = Base.Vector(0,0,0)

#main_triangle_verts     = create_triangle_vertices(penta_radius)
#main_triangle_normal    = main_triangle_verts[1].sub(main_triangle_verts[0]).cross(main_triangle_verts[2].sub(main_triangle_verts[0])).normalize()

main_triangle_verts, main_triangle_normal, rotate_main_verts, rev_rotate_main_verts = create_triangle_vertices(penta_radius)
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

    if 0:
        point0 = Part.makeSphere(5)
        point0.Placement.Base = pcb_triangle_verts[0];
        Part.show(point0)
    
        point1 = Part.makeSphere(2.5)
        point1.Placement.Base = pcb_triangle_verts[1];
        Part.show(point1)

    pcb_led_intersections = []

    for led_location in led_locations:
        i = line_plane_intersection([led_location, center] , pcb_triangle_verts)
        pcb_led_intersections.append(i)

        if None:
            p = Part.makeSphere(1)
            p.Placement.Base = i
            Part.show(p)

if 1:
    # Create LED holes
    led_holes   = []

    led_shaft   = Part.makeBox(led_shaft_height ,led_shaft_width, led_conn_length)
    led_shaft.Placement.Base = Base.Vector(-led_shaft_height/2, -led_shaft_width/2, 0)
    #Part.show(led_shaft)

    center_proj = center.sub(Base.Vector(main_triangle_normal).multiply(main_triangle_normal.dot(center.sub(main_triangle_verts[0]))))
    Draft.makeWire([center, center_proj])

    compensation_angles = []

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
#        App.Console.PrintMessage("angle_to_center:")
#        App.Console.PrintMessage(angle_to_center)
#        App.Console.PrintMessage("\n")
#        App.Console.PrintMessage("i0:")
#        App.Console.PrintMessage(i0)
#        App.Console.PrintMessage("\n")

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
        compensation_angles.append(compensation_angle)

        rotate_z        = App.Rotation(Base.Vector(0,0,1), compensation_angle)
        rotate_final    = rotate_led.multiply(rotate_z)

        loc = Base.Vector(-led_shaft_height/2,-led_shaft_width/2,-(led_height-led_stickout)-led_conn_length)
        loc = rotate_final.multVec(loc)


        led_shaft.Placement.Base     = led_location.add(loc)
        led_shaft.Placement.Rotation = rotate_final

        led_holes.append(led_shaft)

#        Part.show(cyl_big)
#        Part.show(led_shaft)

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
    sphere = cut_plane(sphere, main_triangle_verts, invert = True, translate = -pcb_plane_offset)
    #Part.show(sphere)

if 1: 
    # Cut screw insert holes
    insert_locations = []

    # 3 screw inserts are located in between the location of 3 LED holes of each of the 3 corners
    # Use a weighed average to shift the hole a bit outward.
    insert_locations.append(Base.Vector(pcb_led_intersections[0]).multiply(6).   \
                                add(Base.Vector(pcb_led_intersections[1]).multiply(4)). \
                                add(Base.Vector(pcb_led_intersections[nr_leds_per_side]).multiply(4)). \
                                multiply(1/14))

    insert_locations.append(Base.Vector(pcb_led_intersections[nr_leds_per_side-2]).multiply(4).   \
                                add(Base.Vector(pcb_led_intersections[nr_leds_per_side-1]).multiply(6)). \
                                add(Base.Vector(pcb_led_intersections[2*nr_leds_per_side-2]).multiply(4)). \
                                multiply(1/14))

    t = nr_leds_per_side * (nr_leds_per_side+1)//2

    insert_locations.append(Base.Vector(pcb_led_intersections[t-3]).multiply(4).   \
                                add(Base.Vector(pcb_led_intersections[t-2]).multiply(4)). \
                                add(Base.Vector(pcb_led_intersections[t-1]).multiply(6)). \
                                multiply(1/14))

    # There's also a screw insert right in the center, which is the center of the 3 exterior holes
    insert_locations.append(Base.Vector(pcb_led_intersections[0].add(pcb_led_intersections[nr_leds_per_side-1]).add(pcb_led_intersections[t-1])).multiply(1/3))

    for insert_loc in insert_locations:
        insert_cyl  = Part.makeCylinder(screw_insert_radius, screw_insert_height)
        insert_cyl.Placement.Base = insert_loc
        insert_cyl.Placement.Rotation = App.Rotation(Base.Vector(0,0,1), Base.Vector(-1,0,0))
        sphere = sphere.cut(insert_cyl)

    #Part.show(sphere)

if 1:
    #============================================================
    # Magnet holes and alignment features
    #============================================================

    # In what follows, we create magents and alignment boxes on one side, apply them, and
    # then immediately rotate the part around 2 times so that is also applied to the 
    # other 2 sides.

    s0 = 0
    s1 = 1

    #============================================================
    # Place magnet holes in between the size LED holes
    #============================================================

    rotate_side_normal = main_triangle_verts[s0].cross(main_triangle_verts[s1])
    tetra_side_angle = main_triangle_verts[s0].getAngle(main_triangle_verts[s1])
    boundary_angle = tetra_side_angle / nr_leds_per_side * 1.1

    mag_axis_rotation   = App.Rotation(Base.Vector(0,0,-1), rotate_side_normal)
    mag_axis_radius_adj = (main_triangle_verts[s0].Length - magnet_radius - magnet_dist_from_shell) / main_triangle_verts[s0].Length

    for mag_nr in range(nr_leds_per_side-1):
        rotate_side = App.Rotation(rotate_side_normal, math.degrees(boundary_angle + mag_nr * (tetra_side_angle - 2 * boundary_angle) / (nr_leds_per_side-2)))
        mag_center = rotate_side.multVec(Base.Vector(main_triangle_verts[s0]).multiply(mag_axis_radius_adj))
        mag = Part.makeCylinder(magnet_radius, magnet_height)
        mag.Placement.Base = mag_center
        mag.Placement.Rotation = mag_axis_rotation

        r = App.Rotation(main_triangle_normal, 360/3)
        for i in range(0,3):
            sphere = sphere.cut(mag)
            mag.Placement.Base      = r.multVec(mag.Placement.Base)
            mag.Placement.Rotation  = r.multiply(mag.Placement.Rotation)

    #============================================================
    # Place alignment features
    #============================================================

    # We don't do any chamfering. That needs to be done in postprocessing.

    box_rotation    = mag_axis_rotation
    box_radius_adj  = (main_triangle_verts[s0].Length - magnet_radius - magnet_dist_from_shell) / main_triangle_verts[s0].Length

    # This rotates something on the ray from the center to the corner to the middle.
    rotate_to_middle = App.Rotation(rotate_side_normal, math.degrees(tetra_side_angle/2))

    # I lost track of the different rotation, so I just create a new x/y/z coordinate
    # system that has X going from center to the center magnet, Y from one triangle corner to the next,
    # and Z orthogonal to that.
    x_axis          = rotate_to_middle.multVec(Base.Vector(main_triangle_verts[s0])).normalize()
    y_axis          = Base.Vector(main_triangle_verts[s0]).sub(main_triangle_verts[s1]).normalize()
    z_axis          = x_axis.cross(y_axis).normalize()

    box_sizes       = []
    box_placements  = []
    box_ops         = []

    box_sizes.append( Base.Vector(align_box_size_x, align_box_size_y, align_box_size_z))
    box_placements.append(Base.Vector(-align_box_size_x/2 - magnet_radius - 1, align_box_size_y/2, align_box_size_z/2))
    box_ops.append(-1)

    # Cutouts
    box_sizes.append( Base.Vector(align_box_size_x, align_box_size_y, align_box_size_z))
    box_placements.append(Base.Vector(-align_box_size_x/2 - magnet_radius - 1, align_box_size_y/2, align_box_size_z/2))
    box_ops.append(-1)

    box_sizes.append( Base.Vector(align_box_size_x, align_box_size_y, align_box_size_z))
    box_placements.append(Base.Vector(-3*align_box_size_x/2 - magnet_radius - 1, -align_box_size_y/2, align_box_size_z/2))
    box_ops.append(-1)

    # Extends
    box_sizes.append( Base.Vector(align_box_size_x-0.8, align_box_size_y-0.8, align_box_size_z))
    box_placements.append(Base.Vector(-align_box_size_x/2 - magnet_radius - 1, -align_box_size_y/2, -align_box_size_z/2))
    box_ops.append(1)

    box_sizes.append( Base.Vector(align_box_size_x-0.8, align_box_size_y-0.8, align_box_size_z))
    box_placements.append(Base.Vector(-3*align_box_size_x/2 - magnet_radius - 1, align_box_size_y/2, -align_box_size_z/2))
    box_ops.append(1)

    for b in range(len(box_sizes)):
        box_size = box_sizes[b]
        box_placement = box_placements[b]

        box_offset = Base.Vector(-box_size.x/2, -box_size.y/2, -box_size.z/2).add(box_placement)

        box_offset = Base.Vector(x_axis).multiply(box_offset.x). \
                        add(Base.Vector(y_axis).multiply(box_offset.y)). \
                        add(Base.Vector(z_axis).multiply(box_offset.z))

        # Create a box. Rotate it to the center magnet. Adjust the location from there.
        box = Part.makeBox(box_size.x, box_size.y, box_size.z)
        box_origin = rotate_to_middle.multVec(Base.Vector(main_triangle_verts[s0]).multiply(mag_axis_radius_adj)).add(box_offset)
        
        box.Placement.Base  = box_origin
        box.Placement.Rotation = box_rotation
        #Part.show(box)

        r = App.Rotation(main_triangle_normal, 360/3)
        for i in range(0,3):
            if box_ops[b] == -1:
                sphere = sphere.cut(box)
            else:
                sphere = sphere.fuse(box)
            box.Placement.Base      = r.multVec(box.Placement.Base)
            box.Placement.Rotation  = r.multiply(box.Placement.Rotation)

    pass


if 1:
    #============================================================   
    # PCB
    #============================================================   

    # Make PCB bit smaller than maximum
    # First scale the size of the PCB triangle proportionally with the distance to which the plane has moved from
    # the outside to the center. Then make it 10% smaller with a fudge factor.
    scale_factor = (main_triangle_center.Length - pcb_plane_offset - pcb_thickness) / main_triangle_center.Length * 0.90

    # The 3 coordinates that form the boundaries of the PCB triangle...
    pcb_triangle_verts = [
        Base.Vector(main_triangle_verts[0]).scale(1, scale_factor, scale_factor).sub(Base.Vector(-pcb_plane_offset-pcb_thickness)),
        Base.Vector(main_triangle_verts[1]).scale(1, scale_factor, scale_factor).sub(Base.Vector(-pcb_plane_offset-pcb_thickness)),
        Base.Vector(main_triangle_verts[2]).scale(1, scale_factor, scale_factor).sub(Base.Vector(-pcb_plane_offset-pcb_thickness)),
    ]

    # Create the PCB polygon.
    pcb = Part.makePolygon( [ pcb_triangle_verts[0], pcb_triangle_verts[1], pcb_triangle_verts[2], pcb_triangle_verts[0] ] )
    pcb = Part.Face(pcb)
    pcb = pcb.extrude(Base.Vector(-pcb_thickness, 0,0))

    # LED locations
    for idx, l in enumerate(pcb_led_intersections):
        # The componsation angles that we used for the sphere element can't be reused here, 
        # so just use circular holes instead of boxes for the LED leads. It's only to get an idea. The actual
        # PCB is done in KiCad based on a projection of the sphere element, not on this PCB example.
        cyl = Part.makeCylinder(led_conn_width/2, pcb_thickness)
        cyl.Placement.Base = l
        cyl.Placement.Rotation = App.Rotation(Base.Vector(0,0,1), Base.Vector(1,0,0))
        pcb = pcb.cut(cyl)

    # Insert holes in the PCB for the inner piece feet.
    for l in insert_locations:
        cyl = Part.makeCylinder(pcb_hole_radius, pcb_thickness)
        cyl.Placement.Base = l
        cyl.Placement.Rotation = App.Rotation(Base.Vector(0,0,1), Base.Vector(1,0,0))
        pcb = pcb.cut(cyl)

    # Holes for more inner piece supports
    inner_support_loc = Base.Vector(pcb_led_intersections[nr_leds_per_side//2 -1]).multiply(3).   \
                                add(Base.Vector(pcb_led_intersections[nr_leds_per_side//2]).multiply(3)). \
                                add(Base.Vector(pcb_led_intersections[nr_leds_per_side + nr_leds_per_side//2 -1]).multiply(5)). \
                                multiply(1/11)

    # Create 2 elongated gaps with rounded ends
    gap1 = Part.makeBox(pcb_thickness, pcb_gap_length/2-pcb_gap_width, pcb_gap_width)
    gap1.Placement.Base     = Base.Vector(0, -pcb_gap_length/2, -pcb_gap_width/2)
    cyl = Part.makeCylinder(pcb_gap_width/2, pcb_thickness)
    cyl.Placement.Base     = Base.Vector(0, -pcb_gap_length/2, 0)
    cyl.Placement.Rotation = App.Rotation(Base.Vector(0,0,1), Base.Vector(1,0,0))
    gap1 = gap1.fuse(cyl)
    cyl.Placement.Base     = Base.Vector(0, -pcb_gap_width, 0)
    gap1 = gap1.fuse(cyl)

    gap2 = Part.makeBox(pcb_thickness, pcb_gap_length/2-pcb_gap_width, pcb_gap_width)
    gap2.Placement.Base     = Base.Vector(0, pcb_gap_width, -pcb_gap_width/2)
    cyl = Part.makeCylinder(pcb_gap_width/2, pcb_thickness)
    cyl.Placement.Base     = Base.Vector(0, pcb_gap_length/2, 0)
    cyl.Placement.Rotation = App.Rotation(Base.Vector(0,0,1), Base.Vector(1,0,0))
    gap2 = gap2.fuse(cyl)
    cyl.Placement.Base     = Base.Vector(0, pcb_gap_width, 0)
    gap2 = gap2.fuse(cyl)

    gap1.Placement.Base     = Base.Vector(inner_support_loc)
    gap2.Placement.Base     = Base.Vector(inner_support_loc)

    gap = gap1.fuse(gap2)

    r = App.Rotation(main_triangle_normal, 360/3)
    for i in range(0,3):
        pcb = pcb.cut(gap)
        gap.Placement.Base      = r.multVec(gap.Placement.Base)
        gap.Placement.Rotation  = r.multiply(gap.Placement.Rotation)

if 1:
    #============================================================   
    # Inner piece
    #============================================================   

    # Create supports for inner piece that fits in the gap
    inner_support_length    = pcb_gap_length/2 - pcb_gap_width 
    inner_support_width     = pcb_gap_width - 2 * inner_pcb_gap_margin

    inner_support1                      = Part.makeBox(pcb_thickness + inner_pcb_clearance, inner_support_length, inner_support_width)
    inner_support1.Placement.Base       = Base.Vector(0, -pcb_gap_length/2, -inner_support_width/2)
    cyl                                 = Part.makeCylinder(inner_support_width/2, pcb_thickness + inner_pcb_clearance)
    cyl.Placement.Base                  = Base.Vector(0, -pcb_gap_length/2, 0)
    cyl.Placement.Rotation              = App.Rotation(Base.Vector(0,0,1), Base.Vector(1,0,0))
    inner_support1                      = inner_support1.fuse(cyl)
    cyl.Placement.Base                  = Base.Vector(0, -pcb_gap_width, 0)
    inner_support1                      = inner_support1.fuse(cyl)

    inner_support2                      = Part.makeBox(pcb_thickness + inner_pcb_clearance, inner_support_length, inner_support_width)
    inner_support2.Placement.Base       = Base.Vector(0, pcb_gap_width, -inner_support_width/2)
    cyl                                 = Part.makeCylinder(inner_support_width/2, pcb_thickness + inner_pcb_clearance)
    cyl.Placement.Base                  = Base.Vector(0, pcb_gap_length/2, 0)
    cyl.Placement.Rotation              = App.Rotation(Base.Vector(0,0,1), Base.Vector(1,0,0))
    inner_support2                      = inner_support2.fuse(cyl)
    cyl.Placement.Base                  = Base.Vector(0, pcb_gap_width, 0)
    inner_support2                      = inner_support2.fuse(cyl)

    inner_support1.Placement.Base       = Base.Vector(inner_support_loc)
    inner_support2.Placement.Base       = Base.Vector(inner_support_loc)

    inner_support = inner_support1.fuse(inner_support2)

    points = [
            Base.Vector(insert_locations[0]).add(Base.Vector(pcb_thickness + inner_pcb_clearance,0,0)),  
            Base.Vector(insert_locations[1]).add(Base.Vector(pcb_thickness + inner_pcb_clearance,0,0)),  
            Base.Vector(insert_locations[2]).add(Base.Vector(pcb_thickness + inner_pcb_clearance,0,0)),  
            Base.Vector(insert_locations[0]).add(Base.Vector(pcb_thickness + inner_pcb_clearance,0,0)),  
            ]

    poly = Part.makePolygon(points)
    face = Part.Face(poly)
    inner = face.extrude(Base.Vector(7-pcb_thickness - inner_pcb_clearance, 0, 0))

    inner_feet = []
    for idx, l in enumerate(insert_locations):
        #inner_foot = Part.makeCylinder(inner_foot_radius, screw_insert_height+3)
        inner_foot = Part.makeCylinder(inner_foot_radius, 7)
        inner_foot.Placement.Base = Base.Vector(l)
        inner_foot.Placement.Rotation = App.Rotation(Base.Vector(0,0,1), Base.Vector(1,0,0))
        inner = inner.fuse(inner_foot)

        cyl  = Part.makeCylinder(screw_insert_radius, screw_insert_height)
        cyl.Placement.Base = Base.Vector(l)
        cyl.Placement.Rotation = App.Rotation(Base.Vector(0,0,1), Base.Vector(1,0,0))
        inner = inner.cut(cyl)

    r = App.Rotation(main_triangle_normal, 360/3)
    for i in range(0,3):
        inner = inner.fuse(inner_support)
        inner_support.Placement.Base      = r.multVec(inner_support.Placement.Base)
        inner_support.Placement.Rotation  = r.multiply(inner_support.Placement.Rotation)

    inner.Placement.Rotation = rev_rotate_main_verts
    
    attach_points = [
        rev_rotate_main_verts.multVec(Base.Vector(insert_locations[0]).add(Base.Vector(5))),
        rev_rotate_main_verts.multVec(Base.Vector(insert_locations[1]).add(Base.Vector(5))),
        rev_rotate_main_verts.multVec(Base.Vector(insert_locations[3]).add(Base.Vector(5))),
        ]

    # Attachment point with screw hole
    # There are 3 versions:
    #   - attachment point in the center
    #   - attachment point on the left
    #   - attachment point on the right

    attach_hole_radius  = 1.6
    attach_hole_length  = 9

    attach = Part.makeBox(attach_hole_length, 8, 4)
    cyl = Part.makeCylinder(attach_hole_radius, 4)
    cyl.Placement.Base = Base.Vector(attach_hole_length-2.5, 8/2, 0)
    attach = attach.cut(cyl)

    # Center
    attach.Placement.Base = Base.Vector(attach_points[0].x, 0, attach_points[0].z).add(Base.Vector(0, -8/2, -4))
    inner_center= inner.fuse(attach)

    attach.Placement.Base = Base.Vector(attach_points[0].x, attach_points[0].y * -3/5, attach_points[0].z).add(Base.Vector(0, -8/2, -4))
    inner_left= inner.fuse(attach)

    attach.Placement.Base = Base.Vector(attach_points[0].x, attach_points[0].y * 3/5, attach_points[0].z).add(Base.Vector(0, -8/2, -4))
    inner_right= inner.fuse(attach)


# Rotate back to original position
sphere.Placement.Rotation = rev_rotate_main_verts
pcb.Placement.Rotation = rev_rotate_main_verts
#Part.show(sphere)

if None:
    final_led_coords = []

    for r in range(0,5):
        for l in led_locations:
            lr = rev_rotate_main_verts.multVec(l)

            s = Part.makeSphere(1)
            s.Placement.Base = lr
            Part.show(s)

if True:
    for i in range(0,5):
        r = App.Rotation(Base.Vector(0, 0, 1), i * (360/5)).multiply(rev_rotate_main_verts)
        sphere.Placement.Rotation = r
        Part.show(sphere)

if True:
    for i in range(0,5):
        r = App.Rotation(Base.Vector(1,0,0), 180).multiply(App.Rotation(Base.Vector(0, 0, -1), (i + 0.5) * (360/5))).multiply(rev_rotate_main_verts)
        sphere.Placement.Rotation = r
        Part.show(sphere)

if True:
    for i in range(0,5):
        # For the 63.4... angle, see http://www.rwgrayprojects.com/rbfnotes/polyhed/PolyhedraData/Icosahedron/Icosahedron.pdf 
        r = App.Rotation(Base.Vector(1,0,0), 180).multiply(App.Rotation(Base.Vector(0, 0, -1), i * (360/5))).multiply(rev_rotate_main_verts).multiply(App.Rotation(Base.Vector(0,1,0), -63.434948))
        sphere.Placement.Rotation = r
        Part.show(sphere)

if True:
    for i in range(0,5):
        r = App.Rotation(Base.Vector(0, 0, -1), (i+0.5) * (360/5)).multiply(rev_rotate_main_verts).multiply(App.Rotation(Base.Vector(0,1,0), -63.434948))
        sphere.Placement.Rotation = r
        Part.show(sphere)



#Part.show(pcb)
#Part.show(inner_center)
#Part.show(inner_left)
#Part.show(inner_right)

#Part.show(sphere)

#main_triangle_verts, main_triangle_normal, rev_rotate_main_verts = create_triangle_vertices(penta_radius)


App.ActiveDocument.recompute()
Gui.activeDocument().activeView().viewRight()
Gui.SendMsgToActiveView("ViewFit")

#f = open("C:\\Users\\tverbeure\\projects\\ball\\test.txt", "w")
#f.write("Hello world!\n")
#f.close()

