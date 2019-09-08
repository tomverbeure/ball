
led_coords_fxy = []

led_colors = [ Blue, Cyan, Magenta, Yellow, Black, White, Oak, Pine, Birch, Iron, Steel, Stainless ]

for f, xy in enumerate(healpix_fxy):
    led_coords_xy = []
    for y in xy:
        led_coords_y = []
        for p in y:
            led_coords_y.append([p[0]*sphere_radius, p[1]*sphere_radius, p[2]*sphere_radius])

            scene += color(led_colors[f])(translate(led_coords_y[-1])(sphere(dot_radius, segments=10)))

        led_coords_xy.append(led_coords_y)
    led_coords_fxy.append(led_coords_xy)

boundaries  = color(Yellow)(polyhedron(points=boundary_vecs, faces=boundary_faces))
boundaries += rotate(a=90,v=UP_VEC)(color(Yellow)(polyhedron(points=boundary_vecs, faces=boundary_faces)))
boundaries += rotate(a=180,v=UP_VEC)(color(Yellow)(polyhedron(points=boundary_vecs, faces=boundary_faces)))
boundaries += rotate(a=270,v=UP_VEC)(color(Yellow)(polyhedron(points=boundary_vecs, faces=boundary_faces)))
#boundaries -= sphere(%f,segments=40)\n", sphere_radius * 0.7);

boundaries += rotate(a=00,v=UP_VEC)(color(Yellow)(polyhedron(points=boundary_vecs, faces=boundary_faces)))

scene += boundaries

#scene += color(Yellow)(polyhedron(points=[dot_coords[0], dot_coords[1], dot_coords[3]], faces=[ [0,1,2] ]))

scene += color(Green)(sphere(sphere_radius * 0.9,segments=40))


print(scad_render(scene))
