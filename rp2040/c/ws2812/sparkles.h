#ifndef SPARKLES_H
#define SPARKLES_H

#include <stdio.h>
#include <stdlib.h>

#include "general.h"
#include "pattern.h"

class Sparkles : public Pattern
{
    public:
    void init();
    int calc_next_frame(float offset);
    void render(t_color led_buffer[NUM_PIXELS]);
};

#endif
