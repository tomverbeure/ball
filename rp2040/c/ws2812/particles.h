#ifndef PARTICLES_H
#define PARTICLES_H

#include <stdio.h>
#include <stdlib.h>

#include "general.h"

class Particles
{
    public:

    uint8_t cur_values[NUM_PIXELS];

    void init();
    int calc_next_frame(int dir);
    void render(t_color led_buffer[NUM_PIXELS]);
};



#endif
