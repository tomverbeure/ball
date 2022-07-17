#include <math.h>

#include "lib.h"
#include "rgb_sphere.h"

void RGBSphere::init()
{
}

int RGBSphere::calc_next_frame(float offset)
{
    this->offset = offset;
}

void RGBSphere::render(t_color led_buffer[NUM_PIXELS])
{
    for(int i = 0; i < NUM_PIXELS; ++i){
        const t_led_coord *pos = &led_coords[i];
        
        float r = sin(pos->x * 0.5 * M_PI + offset);
        float g = sin(pos->y * 1.0 * M_PI + offset/3.1);
        float b = sin(pos->z * 2.0 * M_PI + offset/2.3);

        led_buffer[i].r = int((r+1.0) * 112.0) + 16;
        led_buffer[i].g = int((g+1.0) * 112.0) + 16;
        led_buffer[i].b = int((b+1.0) * 112.0) + 16;
    }
}

