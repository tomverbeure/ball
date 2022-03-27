

# Introduction

This project started roughly in the summer of 2019. I've always been fascinated by LED creations: massive LED planes on
buildings with animations that seem to jump out into the 3D world, LED cubes with mesmerizing animations, 
Greg Davil's small size cube and icosahedron at the Hackaday Superconference. There was always the plan to
make something myself, and over the years I assembled nice assortment of LED panels, RGB LED strips, and even a few bags 
of plain vanilla single color through-hole LEDs: the "buy" button on AliExpress is sometimes irresitable. 

But nothing ever came off it, until a bunch of lunch time discussion at work (remember them?) with my friend and
3D printing wizzard Jens about how to approach an LED sphere. The idea is not totally original, but there's surprisingly
little out there, even today, almost 3 years after our first discussions: ... created an wireframe sphere with 192 LEDs, ...
created these 2 geodesic structures that are a close enough approximation. and just a few months ago, ... showed off this 
one. All of these projects are amazing and their creators spent long hours getting it all together. But there's something
about each of them that doesn't quite do it to me: I want an LED sphere that's truly round and that doesn't have one
obvious north-south axis with perpendicular circles around it.

# Deconstruction of a Sphere into Smaller Pieces

An ideal LED sphere has the LEDs evenly distributed of all over the surface: no matter how to rotate the object, or which
angle you look at it, the LEDs are organized exactly the same. There is no top, no bottom, no obvious sub-element around
which the LEDs are organized.

The problem with this is that it is not possible to do this. There are only good approximations.
https://stackoverflow.com/questions/9600801/evenly-distributing-n-points-on-a-sphere

One extremely good such approximation is Fibonacci sphere algorithm. https://openprocessing.org/sketch/41142
https://www.vertexshaderart.com/art/79HqSrQH4meL63aAo/revision/9c9YN5LwBQKLDa4Aa

Another one is the HEALPix algorithm. https://en.wikipedia.org/wiki/HEALPix

Unfortunately, it's one thing to come up with an arrangment that is visually almost perfect, it's another to come
up with something that can be physically created with a reasonable amount of effort. One of my additional constraints
was that the LEDs can be soldered on some kind of PCB: amazing as it is, precision soldering 192 LEDs, or more, is just
not something I'm will to do.

One solution Jens and I looked in to where flex PCBs that are arranged as follows:

I still believe that this solution is very promising, but I decided the reduce the problem even more, and
fall back to a more traditional approach of a polyhedra base with curved shell pieces around it. The LED ball of
... takes that to the extreme in the sense that there isn't a curved surface at all: it's just triangles. 

There are many ways to reduce a sphere into a tesselated polyhedral structure: something as simple as a tetrahedron or 
a cube can work with only 4 or 6 faces, the underlying structure is just too coarse to be visually appealing. The higher
the number of faces, the closer the polyhedron will match an actual sphere, and the better it will look.

https://cage.ugent.be/~hs/polyhedra/polyhedra.html

One of the most common examples is the a regular soccer ball, which uses a truncated icosahdron to approximate
a sphere.

https://en.wikipedia.org/wiki/Truncated_icosahedron

There's also the class of geodesic domes.

...geodesic dome...

There's an important other consideration than just how it looks: the number of unique parts, and the total number
of parts in general. A truncated icosahdron looks great, but it requires 2 different parts and a total of 32 pieces:
20 hexagons and 12 pentagon. It adds to the overall design, solder and assembly work.

...more faces means smaller pieces as well...

In the end, an icosahedron seemed like the best compromise: it's constructed out of identical triangles, and it has 20 face, 
which is low enough to be manageable, yet high enough reduce the angle between LEDs on opposite sides of a single element.

# LED Selection

Most objects with a large amount of LEDs have flat surfaces, which makes it possible to use surface mounted devices.
This makes mass assembly pretty easy, even for hobbyist: you order a PCB with stencil from your favorite PCB provider,
apply solder paste, put things on a hot plate or in a toaster, and you're done.

But a flat surface is not what I wanted, which left me with a number of options:

* use a flex PCB 
* glue individual SMD LEDs onto the sphere and solder them manually
* use through-hole LEDs

Compared to standard PCBs where you can get a whole bunch of just a couple of dollars, Flex PCB are still quite expensive.
And since I've never worked with them before, I almost certainly would need at least one iterations to really get things right.
Hand-soldering wires to hundreds of LEDs was out of the question, so I chose to go with through-hole LEDs.

The next question is about the kind of LEDs: you can go with the low-level 3-in-1 RGB LEDs that shift all the intelligence
to get different color shades to the driving logic, or you can use smart LEDs from the WS2812 class that where you serially
shift 24-bit color values into a chain of LEDs.

WS2812 LEDs are more expensive, they consume more power, and they aren't many thu-hole versions, LCSC only has the WS2812B-F8,
but the fact that you only need 3 pins per PCB is very attractive: it's something you can still do with regular 2.54mm pin
connectors. So that's what I choose.

As for size, I choose the WS2812B-F8 over the WS2812B-F5. The F8 has an 8mm main diameter versus 5mm for the F5, so the F5 seems
at first more attractive 


# Design of a Sphere with an Icosahedron Base

# LED Distribution within each Triangular Element

So the decision was made to go with an icosahedron 




* 194 LED sphere

    * [Youtube](https://www.youtube.com/watch?v=Q5d8gTppuYo)

* LED foldable spheres

    * [Youtube](https://www.youtube.com/watch?v=3ijp2IU6-3s)

* Interactive Geodesic LED dome

    120 lights.

    Uniform triangles -> non-uniforms LEDs

    * [Youtube](https://www.youtube.com/watch?v=E2HVLBBQtZI)
    * [Instructables](https://www.instructables.com/Interactive-Geodesic-LED-Dome/)

* Geodesic(k) RGB LED Spheres

    Uses 18650 batteries spotwelded together.

    Small: 80 LEDs. Large: 180 LEDs.

    * [Prusaprinters.org](https://www.prusaprinters.org/prints/40182-geodesick-rgb-led-spheres))


* Battery

    * 18650 cells. What configuration?

        e.g 2s4p

    * TP4056 charger module

    * [How to charge li-ion battery pack using IMAX b6 18650 lipo charger](https://www.youtube.com/watch?v=m5V4MG0WZF4)
