
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

    float dot_radius = 0.1;
    float sphere_radius = 10;

    printf("# npix: %d\n", npix);
    printf("from solid import *\n\n");
    printf("from solid.utils import *\n\n");

    printf("dot_coords = []\n");
    printf("dots = []\n");

    double *vecs = malloc(npix * sizeof(double) * 3);

    int pix_per_face = npix/12;

    for(int i=0;i<npix;++i){
        double *vec = &vecs[i*3];
        pix2vec_nest(nside, i, vec);
        //pix2vec_ring(nside, i, vec);

        printf("dot_coords.append([%f,%f,%f])\n", vec[0]*sphere_radius, vec[1]*sphere_radius, vec[2]*sphere_radius);

        printf("dots.append(translate(dot_coords[%d])(sphere(%f, segments=10)))\n", i, dot_radius);

        if (i==0){
            printf("scene = color(Black)(dots[0])\n");
        }
        else{
            printf("scene += color(%s)(dots[%d])\n",
                    i==xyf2nest(nside, nside-1,       0, 0) ? "Red" :
                    i==xyf2nest(nside,       0, nside-1, 0) ? "Red" :
                    i==xyf2nest(nside, nside-1, nside-1, 0) ? "Red" :

                    i==xyf2nest(nside,       0,       0, 1) ? "Black" :
                    i==xyf2nest(nside, nside-1,       0, 1) ? "Blue" :
                    i==xyf2nest(nside,       0, nside-1, 1) ? "Blue" :
                    i==xyf2nest(nside, nside-1, nside-1, 1) ? "Blue" :

                    i<   pix_per_face  ? "Blue"      :
                    i< 2*pix_per_face  ? "Cyan"      :
                    i< 3*pix_per_face  ? "Magenta"   :
                    i< 4*pix_per_face  ? "Yellow"    :
                    i< 5*pix_per_face  ? "Black"     :
                    i< 6*pix_per_face  ? "White"     :
                    i< 7*pix_per_face  ? "Oak"       :
                    i< 8*pix_per_face  ? "Pine"      :
                    i< 9*pix_per_face  ? "Birch"     :
                    i<10*pix_per_face  ? "Iron"      :
                    i<11*pix_per_face  ? "Steel"     :
                                         "Stainless"
                              , i);
        }
    }

    printf("boundary_vecs = [ [0,0,0] ]\n");

    double boundary_radius = sphere_radius * 1.2;

    for(int i=0; i<nside;++i){
        double left_vec[3];
        double right_vec[3];
        double middle_vec[3];

        pix2vec_nest(nside, xyf2nest(nside, nside-1, i, 0), left_vec);
        pix2vec_nest(nside, xyf2nest(nside, i, nside-1, 1), right_vec);

        for(int j=0;j<3;j++){
            middle_vec[j] = (left_vec[j] + right_vec[j])/2;
        }

        printf("boundary_vecs.append([%f,%f,%f])\n", middle_vec[0] * boundary_radius, middle_vec[1] * boundary_radius, middle_vec[2] * boundary_radius);
        printf("scene += color(Iron)(translate(boundary_vecs[-1])(sphere(%f, segments=10)))\n", dot_radius);
    }

    for(int i=0; i<nside;++i){
        double left_vec[3];
        double right_vec[3];
        double middle_vec[3];

        pix2vec_nest(nside, xyf2nest(nside, i, 0, 0), left_vec);
        pix2vec_nest(nside, xyf2nest(nside, i, nside-1, 5), right_vec);

        for(int j=0;j<3;j++){
            middle_vec[j] = (left_vec[j] + right_vec[j])/2;
        }

        printf("boundary_vecs.append([%f,%f,%f])\n", middle_vec[0] * boundary_radius, middle_vec[1] * boundary_radius, middle_vec[2] * boundary_radius);
        printf("scene += color(Iron)(translate(boundary_vecs[-1])(sphere(%f, segments=10)))\n", dot_radius);
    }

    for(int i=0; i<nside;++i){
        double left_vec[3];
        double right_vec[3];
        double middle_vec[3];

        pix2vec_nest(nside, xyf2nest(nside, 0, i, 0), left_vec);
        pix2vec_nest(nside, xyf2nest(nside, nside-1, i, 4), right_vec);

        for(int j=0;j<3;j++){
            middle_vec[j] = (left_vec[j] + right_vec[j])/2;
        }

        printf("boundary_vecs.append([%f,%f,%f])\n", middle_vec[0] * boundary_radius, middle_vec[1] * boundary_radius, middle_vec[2] * boundary_radius);
        printf("scene += color(Iron)(translate(boundary_vecs[-1])(sphere(%f, segments=10)))\n", dot_radius);
    }

    for(int i=0; i<nside;++i){
        double left_vec[3];
        double right_vec[3];
        double middle_vec[3];

        pix2vec_nest(nside, xyf2nest(nside, i, nside-1, 0), left_vec);
        pix2vec_nest(nside, xyf2nest(nside, nside-1, i, 3), right_vec);

        for(int j=0;j<3;j++){
            middle_vec[j] = (left_vec[j] + right_vec[j])/2;
        }

        //printf("scene += color(Red)(translate([%f,%f,%f])(sphere(%f, segments=10)))\n", left_vec[0] *sphere_radius, left_vec[1] *sphere_radius, left_vec[2] *sphere_radius,dot_radius);
        //printf("scene += color(Red)(translate([%f,%f,%f])(sphere(%f, segments=10)))\n", right_vec[0] *sphere_radius, right_vec[1] *sphere_radius, right_vec[2] *sphere_radius,dot_radius);
        //printf("scene += color(Iron)(translate([%f,%f,%f])(sphere(%f, segments=10)))\n", middle_vec[0] *sphere_radius, middle_vec[1] *sphere_radius, middle_vec[2] *sphere_radius,dot_radius);

        printf("boundary_vecs.append([%f,%f,%f])\n", middle_vec[0] * boundary_radius, middle_vec[1] * boundary_radius, middle_vec[2] * boundary_radius);
        printf("scene += color(Iron)(translate(boundary_vecs[-1])(sphere(%f, segments=10)))\n", dot_radius);
    }


#if 0
    double boundary_vec0[3];
    pix2vec_nest(nside*4, xyf2nest(nside*4, 0, 0, 0), boundary_vec0);

    double boundary_vec1[3];
    pix2vec_nest(nside*4, xyf2nest(nside*4, nside*4-1, 0, 0), boundary_vec1);

    double boundary_vec2[3];
    pix2vec_nest(nside*4, xyf2nest(nside*4, nside*4-1, nside*4-1, 0), boundary_vec2);

    double boundary_vec3[3];
    pix2vec_nest(nside*4, xyf2nest(nside*4, 0, nside*4-1, 0), boundary_vec3);

    printf("boundary_vecs.append([%f,%f,%f])\n", boundary_vec0[0] * boundary_radius, boundary_vec0[1] * boundary_radius, boundary_vec0[2] * boundary_radius);
    printf("boundary_vecs.append([%f,%f,%f])\n", boundary_vec1[0] * boundary_radius, boundary_vec1[1] * boundary_radius, boundary_vec1[2] * boundary_radius);
    printf("boundary_vecs.append([%f,%f,%f])\n", boundary_vec2[0] * boundary_radius, boundary_vec2[1] * boundary_radius, boundary_vec2[2] * boundary_radius);
    printf("boundary_vecs.append([%f,%f,%f])\n", boundary_vec3[0] * boundary_radius, boundary_vec3[1] * boundary_radius, boundary_vec3[2] * boundary_radius);

    printf("scene += color(Magenta)(translate(boundary_vecs[1])(sphere(%f, segments=10)))\n", dot_radius);
    printf("scene += color(Magenta)(translate(boundary_vecs[2])(sphere(%f, segments=10)))\n", dot_radius);
    printf("scene += color(Magenta)(translate(boundary_vecs[3])(sphere(%f, segments=10)))\n", dot_radius);
    printf("scene += color(Magenta)(translate(boundary_vecs[4])(sphere(%f, segments=10)))\n", dot_radius);

    //printf("scene += color(Yellow)(polyhedron(points=boundary_vecs, faces=[ [0,1,2], [0,2,3], [0,3,4], [0,4,1], [1,2,4], [3,4,2] ]))\n");
#endif

    printf("scene += color(Yellow)(polyhedron(points=[dot_coords[0], dot_coords[1], dot_coords[3]], faces=[ [0,1,2] ]))\n");

    printf("scene += color(Green)(sphere(%f,segments=40))\n", sphere_radius-0.0);


    printf("print(scad_render(scene))\n");
}


