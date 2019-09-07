
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <inttypes.h>

#include "chealpix.h"


int main(int argc, char **argv)
{
    int nside = atoi(argv[1]);

    int npix = nside2npix(nside);

    float dot_radius = 0.2;
    float sphere_radius = 5;

    //printf("npix: %d\n", npix);

    printf("from solid import *\n\n");
    printf("from solid.utils import *\n\n");

    printf("dot_coords = []\n");
    printf("dots = []\n");

    double *vecs = malloc(npix * sizeof(double) * 3);

    for(int i=0;i<npix;++i){
        double *vec = &vecs[i*3];
        pix2vec_nest(nside, i, vec);
        //pix2vec_ring(nside, i, vec);

        printf("dot_coords.append([%f,%f,%f])\n", vec[0]*sphere_radius, vec[1]*sphere_radius, vec[2]*sphere_radius);

        printf("dots.append(translate(dot_coords[%d])(sphere(%f, segments=20)))\n", i, dot_radius);

        if (i==0){
            printf("scene = color(Blue)(dots[0])\n");
        }
        else{
            printf("scene += color(%s)(dots[%d])\n", 
                    i<  npix/12   ? "Blue"  :
                    i< 2*npix/12  ? "Cyan"   :
                    i< 3*npix/12  ? "Magenta":
                    i< 4*npix/12  ? "Yellow"   :
                    i< 5*npix/12  ? "Black"   :
                    i< 6*npix/12  ? "White"   :
                    i< 7*npix/12  ? "Oak"   :
                    i< 8*npix/12  ? "Pine"   :
                    i< 9*npix/12  ? "Birch"   :
                    i<10*npix/12  ? "Iron"   :
                    i<11*npix/12  ? "Steel"   :
                                    "Stainless"
                              , i);
        }
    }

    printf("scene += color(Red)(polyhedron(points=[dot_coords[0], dot_coords[1], dot_coords[3]], faces=[ [0,1,2] ]))\n");

    printf("scene += color(Green)(sphere(%f,segments=40))\n", sphere_radius);

    printf("print(scad_render(scene))\n");
}


