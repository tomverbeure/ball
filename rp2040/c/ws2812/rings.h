#ifndef RINGS_H
#define RINGS_H

#include <stdio.h>
#include <stdlib.h>

#include "general.h"
#include "pattern.h"

class Rings : public Pattern
{
    public:
    t_vec       start;
    t_vec       dir;
    t_color     color;
    int         nr_rings;
    float       ring_thickness;
    float       spacing_thickness;

    t_plane     plane;
    float       offset;

    void init();
    int calc_next_frame(float offset);
    void render(t_color led_buffer[NUM_PIXELS]);
};

#endif
