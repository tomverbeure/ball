
# LED Sphere

* Isosahedron: 20 triangular faces

   Progression: 1, 1+3 = 4, 4 + 5 = 9, 9 + 7 = 16, 16 + 9 = 25, 25 + 11 = 36, 36 + 13 = 49

   * 1 triangle -> 1 triangle:    20 faces
   * 1 triangle -> 4 triangles:   80 faces
   * 1 triangle -> 9 triangles:  180 faces
   * 1 triangle -> 16 triangles: 320 faces
   * 1 triangle -> 25 triangles: 500 faces

Possibilities:

    * 80 faces, but divide each face into 16 LEDs -> 1280 LEDs
    * 80 faces, but divide each face into 25 LEDs -> 2000 LEDs
    * 80 faces, but divide each face into 36 LEDs -> 2880 LEDs
    * 80 faces, but divide each face into 49 LEDs -> 3920 LEDs



# References

* [Geodesic(k) LED Spheres](https://blog.arduino.cc/2020/09/21/these-rgb-led-geodesic-spheres-are-stunning/)

    * [Build instructions](https://www.prusaprinters.org/prints/40182-geodesick-rgb-led-spheres)

* [Construct an icosahedron](https://www.youtube.com/watch?v=biq_SXjaoRU)

* [Construct an icosahedron in FreeCAD](https://www.youtube.com/watch?v=1VXpUjMM-_c)

* [Construction of regular icosahedron within a given sphere](https://proofwiki.org/wiki/Construction_of_Regular_Icosahedron_within_Given_Sphere)

    "From this it is manifest that the square on the diameter of the sphere is five times 
    the square on the radius of the circle from which the icosahedron has been described, 
    and that the diameter of the sphere is composed of the side of the hexagon and two of 
    the sides of the decagon inscribed in the same circle."

    Dsphere^2 = 5 * (Rhex^2)

    Rhex = sqrt(Dsphere^2/5) = Dsphere/sqrt(5) = 2 * Rsphere / sqrt(5)

* [Ad Quadratum Construction and Study of the Regular Polyhedra](http://www.lemeestudies.com/Misc/14.millennium_sphere/products/AdQuadratum.pdf)

