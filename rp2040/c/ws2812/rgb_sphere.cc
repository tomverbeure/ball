#include <math.h>

#include "lib.h"
#include "rgb_sphere.h"

void RGBSphere::init()
{
    rotation_matrix(rot_matrix, 0,0,0);
}

int RGBSphere::calc_next_frame(float offset)
{
    this->offset = offset;
}

void RGBSphere::render(t_color led_buffer[NUM_PIXELS])
{
    rotation_matrix(rot_matrix, offset, offset,offset);

    for(int i = 0; i < NUM_PIXELS; ++i){
        const t_led_coord *pos = &led_coords[i];

        t_vec p = matrix_mul_vec(rot_matrix, *pos);
        
        float r = sin(p.x * 1.0 * M_PI + offset);
        float g = sin(p.y * 1.0 * M_PI + offset*2);
        float b = sin(p.z * 1.0 * M_PI + offset*3);

        led_buffer[i].r = int((r+1.0) * 112.0) + 16;
        led_buffer[i].g = int((g+1.0) * 112.0) + 16;
        led_buffer[i].b = int((b+1.0) * 112.0) + 16;
    }
}

