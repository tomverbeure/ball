
boundaries  = color(Yellow)(polyhedron(points=boundary_vecs, faces=boundary_faces))
boundaries += rotate(a=90,v=UP_VEC)(color(Yellow)(polyhedron(points=boundary_vecs, faces=boundary_faces)))
boundaries += rotate(a=180,v=UP_VEC)(color(Yellow)(polyhedron(points=boundary_vecs, faces=boundary_faces)))
boundaries += rotate(a=270,v=UP_VEC)(color(Yellow)(polyhedron(points=boundary_vecs, faces=boundary_faces)))
#boundaries -= sphere(%f,segments=40)\n", sphere_radius * 0.7);

boundaries += rotate(a=00,v=UP_VEC)(color(Yellow)(polyhedron(points=boundary_vecs, faces=boundary_faces)))

scene += boundaries

scene += color(Yellow)(polyhedron(points=[dot_coords[0], dot_coords[1], dot_coords[3]], faces=[ [0,1,2] ]))

scene += color(Green)(sphere(sphere_radius * 0.9,segments=40))


print(scad_render(scene))
