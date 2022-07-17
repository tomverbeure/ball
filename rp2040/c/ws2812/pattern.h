#ifndef PATTERN_H
#define PATTERN_H

#include <stdio.h>
#include <stdlib.h>

#include "general.h"

class Pattern
{
    virtual void init() = 0;
    virtual int calc_next_frame(float offset) = 0;
    virtual void render(t_color led_buffer[NUM_PIXELS]) = 0;
    //virtual void render_phys(t_color led_buffer);
};

#endif
