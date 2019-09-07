
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

    float dot_radius = 0.5;
    float sphere_radius = 5;

    //printf("npix: %d\n", npix);

    printf("from solid import *\n\n");

    for(int i=0;i<npix;++i){
        double vec[3];
        pix2vec_ring(nside, i, vec);

        printf("dot%d = translate([%f,%f,%f])(sphere(%f, segments=20))\n", i, vec[0]*sphere_radius, vec[1]*sphere_radius, vec[2]*sphere_radius, dot_radius);

        if (i==0){
            printf("scene = dot0\n");
        }
        else{
            printf("scene += dot%d\n", i);
        }
    }

    printf("print(scad_render(scene))\n");
}


