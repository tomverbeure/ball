#include "rings.h"

#include "lib.h"

void Rings::init()
{
}

int Rings::calc_next_frame(float offset)
{
    plane.point     = vec_plus_vec(start, vec_mul_scalar(dir, offset));
    plane.normal    = vec_normalize(dir);

    this->offset     = offset;

    return 0;
}

void Rings::render(t_color led_buffer[NUM_PIXELS])
{
    for(int i = 0; i < NUM_PIXELS; ++i){
        const t_led_coord *pos = &led_coords[i];

        float d = distance_plane_point(plane, *pos);
        float total_thickness = ring_thickness + spacing_thickness;
        float segment = floorf(d/total_thickness);
        t_color c;
        if (d<0 || segment >= nr_rings){
            c = black;
        }
        else{
            d = d - segment * total_thickness;
            c = d < ring_thickness ? color : black;
        }

        led_buffer[i] = c;
    }
}
