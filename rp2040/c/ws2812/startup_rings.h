#ifndef STARTUP_RINGS_H
#define STARTUP_RINGS_H

#include <stdio.h>
#include <stdlib.h>

#include "general.h"
#include "rings.h"

class StartupRings : public Rings
{
    public:
    typedef Rings super;

    float   total_thickness;
    float   speed;
    float   offset;

    const t_vec starts[6] = { 
            { -1.0,  0.0,  0.0 },
            {  1.0,  0.0,  0.0 },
            {  0.0, -1.0,  0.0 },
            {  0.0,  1.0,  0.0 },
            {  0.0,  0.0, -1.0 },
            {  0.0,  0.0,  1.0 } };
    const t_color cols[6] = { red, red, green, green, blue, blue };

    int phase_cntr;

    void init() {
        phase_cntr  = 0;

        nr_rings = 3;
        ring_thickness = 0.15;
        spacing_thickness = 0.4;

        total_thickness = (nr_rings * ring_thickness) + ((nr_rings-1) * spacing_thickness);
        speed = 0.1;

        offset = -total_thickness-speed;


        super::init();
    }

    bool calc_next_frame(){
        start = starts[phase_cntr];
        dir = vec_mul_scalar(start, -1);
        color = cols[phase_cntr];

        super::calc_next_frame(offset);
        offset += speed;

        if (offset >= 2){
            ++phase_cntr;
            offset = -total_thickness-speed;
        }

        return phase_cntr >= 6;
    }
};

#endif
