#ifndef RANDOM_RINGS_H
#define RANDOM_RINGS_H

#include <stdio.h>
#include <stdlib.h>

#include "general.h"
#include "rings.h"

class RandomRings : public Rings
{
    public:
    typedef Rings super;

    float   total_thickness;
    float   speed;
    float   offset;

    void init() {
        this->color = { (uint8_t)rnd(), (uint8_t)rnd(), (uint8_t)rnd() };

        this->start.x = frnd(-1.0, 1.0);
        this->start.y = frnd(-1.0, 1.0);
        this->start.z = frnd(-1.0, 1.0);
        this->start = vec_normalize(this->start);
        this->dir = vec_mul_scalar(this->start, -1.0);

        this->ring_thickness = frnd(0.1, 1.0);
        this->spacing_thickness = frnd(0.3, 0.5);
        this->nr_rings = (rnd() % 2)+1;

        this->total_thickness = (this->nr_rings * this->ring_thickness) + ((this->nr_rings-1) * this->spacing_thickness);
        this->speed = frnd(0.06, 0.15);

        this->offset = -total_thickness-speed;

        super::init();
    }

    bool calc_next_frame(){
        super::calc_next_frame(this->offset);
        this->offset += speed;

        return offset >= 2;
    }
};

#endif
