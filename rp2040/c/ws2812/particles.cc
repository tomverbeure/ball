#include "particles.h"

#include "lib.h"

void Particles::init()
{
    for(int i=0;i<NUM_PIXELS;++i){
        cur_values[i] = 0;
    }

    // Populate 60 random LEDs
    for(int i=0;i<120;++i){
        int idx;
        do{
            idx = rnd() % NUM_PIXELS;
        }
        while(cur_values[idx] != 0);
        cur_values[idx] = rnd_whitened(3);
    }
}

int Particles::calc_next_frame(t_vec gravity)
{

    for(int cur_led_idx=0;cur_led_idx<NUM_PIXELS;++cur_led_idx){
        const t_vec &cur_led = led_coords[cur_led_idx];
        float chances[6] = { 0,0,0,0,0,0};
        float cumul_chance = 0.0;
        int num_candidates = 0;

        for(int i=0; i<6;++i){
            // Find all LEDs that are lower. And for those,
            // determine the chance that it will be the chosen one.
            // For now, it's simply the one that is most straight
            // below.
            int cl_led_idx = closest_leds[cur_led_idx][i];
            if (cur_values[cl_led_idx] != 0){
                continue;
            }

            const t_vec &cl_led = led_coords[cl_led_idx];

            t_vec diff = vec_sub_vec(cl_led, cur_led);
            float chance = vec_dot_vec(diff, gravity);

            if (chance >= 0.0){
                ++num_candidates;
                chances[i] = chance;
                cumul_chance += chance;
            }
        }

        // Select weighed random LED out of those that are below:
        if (num_candidates > 0){
            float sel = frnd(0.0, cumul_chance);
            for(int i=0;i<6;++i){
                if (sel < chances[i]){
                    cur_values[closest_leds[cur_led_idx][i]] = cur_values[cur_led_idx];
                    cur_values[cur_led_idx] = 0;
                    break;
                }
            }
        }
    }

    return 0;
}

void Particles::render(t_color led_buffer[NUM_PIXELS])
{
    const t_color color_table[8] = {
        white,
        red,
        green,
        blue,
        cyan,
        yellow,
        orange,
        purple
    };

    for(int i=0;i<NUM_PIXELS;++i){
        if (cur_values[i] != 0){
            led_buffer[calc_phys_led_nr(i)] = color_table[cur_values[i]];
        }
        else{
            led_buffer[calc_phys_led_nr(i)] = black;
        }
    }
}
