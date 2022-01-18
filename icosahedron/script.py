
# import runpy
# runpy.run_path(path_name='C:\\Users\\tom_v\\projects\\ball\\icosahedron\\script.py') 

import math
import Part
from FreeCAD import Base
import FreeCADGui as Gui

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

center = Base.Vector(0,0,0)
main_triangle_verts = [
        Base.Vector( -math.cos(penta_inner_angle/2) * penta_radius,  math.sin(penta_inner_angle/2) * penta_radius,  penta_radius/2 ),
        Base.Vector( -math.cos(penta_inner_angle/2) * penta_radius, -math.sin(penta_inner_angle/2) * penta_radius,  penta_radius/2 ),
        Base.Vector( -math.cos(penta_inner_angle/2) * penta_radius, 0,                                             -penta_radius/2 )
        ]

main_triangle_edges = [
            Part.makeLine( main_triangle_verts[0], main_triangle_verts[1] ),
            Part.makeLine( main_triangle_verts[1], main_triangle_verts[2] ),
            Part.makeLine( main_triangle_verts[2], main_triangle_verts[0] )
        ]
main_triangle_wires = Part.Wire(main_triangle_edges)

top_triangle_edges = [ main_triangle_edges[0], 
                       Part.makeLine( main_triangle_verts[0], center),
                       Part.makeLine( main_triangle_verts[1], center)
        ]
top_triangle_wires = Part.Wire(top_triangle_edges)

side_triangle0_edges = [ 
            Part.makeLine(main_triangle_verts[0], center), 
            Part.makeLine(main_triangle_verts[2], center), 
            Part.makeLine(main_triangle_verts[2], main_triangle_verts[0]) 
        ]
side_triangle0_wires = Part.Wire(side_triangle0_edges)

side_triangle1_edges = [ 
            Part.makeLine(main_triangle_verts[1], center), 
            Part.makeLine(main_triangle_verts[2], center), 
            Part.makeLine(main_triangle_verts[2], main_triangle_verts[1]) 
        ]
side_triangle1_wires = Part.Wire(side_triangle1_edges)

main_triangle   = Part.Face(main_triangle_wires)
top_triangle    = Part.Face(top_triangle_wires)
side_triangle0  = Part.Face(side_triangle0_wires)
side_triangle1  = Part.Face(side_triangle1_wires)

tetra_shell = Part.makeShell([ main_triangle, top_triangle, side_triangle0, side_triangle1])
tetra       = Part.makeSolid(tetra_shell)

#gad = Gui.activeDocument()
#v = gad.getObject(main_triangle.Name)
#v.ShapeColor
#v.ShapeColor = (0.5, 0, 0.5)

#Part.show(main_triangle)
#Part.show(top_triangle)
#Part.show(side_triangle0)
#Part.show(side_triangle1)
#Part.show(tetra_shell)
Part.show(tetra)


