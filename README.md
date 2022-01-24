
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

* 20 faces printed.

	* 4-sided triangle: 10 LEDs -> 200 LEDs
	* 5-sided triangle: 15 LEDs
	* 6-sided triangle: 21 LEDs
	* 7-sided triangle: 27 LEDs
	* 8-sided triangle: 35 LEDs -> 700 LEDs

# Plug-in LEDs

* WS2812D-F8: $0.11 for 100+  

	* inner diameter: 8.0mm, outer diameter: 9.2mm
 	* [datasheet](https://datasheet.lcsc.com/lcsc/1811021523_Worldsemi-WS2812D-F8_C139126.pdf)
	* [LCSC](https://lcsc.com/product-detail/Light-Emitting-Diodes-span-style-background-color-ff0-LED-span_Worldsemi-WS2812D-F8_C139126.html)
	* 3.5V -> 5.3V
	* Needs capacitor and 75 Ohm resistor between VDD/GND per LED

* 



# References

* [Geodesic(k) LED Spheres](https://blog.arduino.cc/2020/09/21/these-rgb-led-geodesic-spheres-are-stunning/)

    * [Build instructions](https://www.prusaprinters.org/prints/40182-geodesick-rgb-led-spheres)

* [Construct an icosahedron](https://www.youtube.com/watch?v=biq_SXjaoRU)

* [Construct an icosahedron in FreeCAD](https://www.youtube.com/watch?v=1VXpUjMM-_c)

* [Construction of regular icosahedron within a given sphere](https://proofwiki.org/wiki/Construction_of_Regular_Icosahedron_within_Given_Sphere)

    "From this it is manifest that the square on the diameter of the sphere is five times 
    the square on the radius of the circle from which the icosahedron has been described, 
    and that the diameter of the sphere is composed of the side of the pentagon and two of 
    the sides of the decagon inscribed in the same circle."

    Dsphere^2 = 5 * (Rpent^2)

    Rpent = sqrt(Dsphere^2/5) = Dsphere/sqrt(5) = 2 * Rsphere / sqrt(5)

* [Ad Quadratum Construction and Study of the Regular Polyhedra](http://www.lemeestudies.com/Misc/14.millennium_sphere/products/AdQuadratum.pdf)

* [Freecad scripting tutorial](https://wiki.freecadweb.org/Python_scripting_tutorial)

* [Freecad Topological data scripting](https://wiki.freecadweb.org/Topological_data_scripting)


# FreeCAD comments

* Base.Vector getAngle -> radians, all other functions -> degrees
* Simply viewing actions, such as aligning view to face are not present out of the box
* aligning a object along an axis is broken.
* Location of buttons in the toolbar always changes
* Add spheres for orientation
* FreeCAD over OpenSCAD: interactivity
* The number of LEDs must be chosen so that there's room in the center for a screw.

