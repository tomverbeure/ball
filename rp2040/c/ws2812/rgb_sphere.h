#ifndef RGB_SPHERE_H
#define RGB_SPHERE_H

#include <stdio.h>
#include <stdlib.h>

#include "general.h"
#include "pattern.h"

class RGBSphere : public Pattern
{
    public:
    float offset;

    void init();
    int calc_next_frame(float offset);
    void render(t_color led_buffer[NUM_PIXELS]);
};

#endif
