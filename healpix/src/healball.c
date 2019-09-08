
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

    //============================================================
    // Healpix coordinates for unity sphere
    //============================================================
    printf("healpix_fxy = []\n");
    for(int f=0;f<12;f++){

        printf("healpix_xy = []\n");
        for(int x=0;x<nside;x++){

            printf("healpix_y = []\n");
            for(int y=0;y<nside;y++){
                double vec[3];
                pix2vec_nest(nside, xyf2nest(nside, x, y, f), vec);

                printf("healpix_y.append([%f,%f,%f])\n", vec[0], vec[1], vec[2]);
            }

            printf("healpix_xy.append(healpix_y)\n");
        }

        printf("healpix_fxy.append(healpix_xy)\n");
    }


    printf("sphere_radius = %f\n", sphere_radius);
    printf("dot_radius = %f\n", dot_radius);

    printf("scene = color(Black)()\n");


    printf("boundary_vecs = [ [0,0,0] ]\n");

    double boundary_radius = sphere_radius * 1.0;

    for(int i=nside-1; i>=0;--i){
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

    for(int i=nside-1; i>=0;--i){
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

        printf("boundary_vecs.append([%f,%f,%f])\n", middle_vec[0] * boundary_radius, middle_vec[1] * boundary_radius, middle_vec[2] * boundary_radius);
        printf("scene += color(Iron)(translate(boundary_vecs[-1])(sphere(%f, segments=10)))\n", dot_radius);
    }

    printf("boundary_faces=[]\n");
    for(int i=1;i<4*nside;++i){
        printf("boundary_faces.append([0,%d,%d])\n",i,i+1);
    }
    printf("boundary_faces.append([0,%d,1])\n",4*nside);

    printf("boundaries  = color(Yellow)(polyhedron(points=boundary_vecs, faces=boundary_faces))\n");
    printf("boundaries += rotate(a=90,v=UP_VEC)(color(Yellow)(polyhedron(points=boundary_vecs, faces=boundary_faces)))\n");
    printf("boundaries += rotate(a=180,v=UP_VEC)(color(Yellow)(polyhedron(points=boundary_vecs, faces=boundary_faces)))\n");
    printf("boundaries += rotate(a=270,v=UP_VEC)(color(Yellow)(polyhedron(points=boundary_vecs, faces=boundary_faces)))\n");
    //printf("boundaries -= sphere(%f,segments=40)\n", sphere_radius * 0.7);
    
    printf("boundaries += rotate(a=00,v=UP_VEC)(color(Yellow)(polyhedron(points=boundary_vecs, faces=boundary_faces)))\n");



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

}


