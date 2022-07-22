#ifndef PRIDE_FLAG_H
#define PRIDE_FLAG_H

#include <stdio.h>
#include <stdlib.h>

#include "general.h"
#include "pattern.h"

class PrideFlag : public Pattern
{
    public:
    t_vec       start;
    t_vec       dir;
    float       ring_thickness;
    float       spacing_thickness;

    t_plane     plane;
    float       offset;

    t_color     flag_colors[11] = {
        // Pride
        { 0xe5, 0x00, 0x00 },
        { 0xff, 0x8d, 0x00 },
        { 0xff, 0xee, 0x00 },
        { 0x02, 0x81, 0x21 },
        { 0x00, 0x4c, 0xff },
        { 0x76, 0x00, 0x88 },
        // Trans
        { 0xff, 0xff, 0xff },
        { 0xff, 0xaf, 0xc7 },
        { 0x73, 0xd7, 0xee },
        { 0x61, 0x39, 0x15 },
        { 0x00, 0x0, 0x000 }
    };

    void init();
    int calc_next_frame(float offset);
    void render(t_color led_buffer[NUM_PIXELS]);
};

#endif
