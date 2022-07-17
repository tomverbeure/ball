
#include "lib.h"
#include "pride_flag.h"

void PrideFlag::init()
{
    start = { 0.0, 0.0, 1.0 };
    dir   = { 0.0, 0.0, -1.0 };
}

int PrideFlag::calc_next_frame(float offset)
{
    plane.point     = vec_plus_vec(start, vec_mul_scalar(dir, offset));
    plane.normal    = vec_normalize(dir);

    this->offset     = offset;

    return 0;
}

void PrideFlag::render(t_color led_buffer[NUM_PIXELS])
{
    for(int i = 0; i < NUM_PIXELS; ++i){
        const t_led_coord *pos = &led_coords[i];

        float d = pos->z;

        t_color c = flag_colors[int((d+1.0)*3+offset) % 11];
        led_buffer[i] = c;
    }
}

