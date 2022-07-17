
#include "lib.h"
#include "sparkles.h"

void Sparkles::init()
{
}

int Sparkles::calc_next_frame(float offset)
{
}

void Sparkles::render(t_color led_buffer[NUM_PIXELS])
{
    for(int i = 0; i < NUM_PIXELS; ++i){
        led_buffer[i] = rand() % 16 ? black : white;
    }
}

