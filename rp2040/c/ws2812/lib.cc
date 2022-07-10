#include "lib.h"

#include "hardware/regs/rosc.h"
#include "hardware/regs/addressmap.h"

uint32_t rnd(int nr_bits){
    int k, random=0;
    volatile uint32_t *rnd_reg=(uint32_t *)(ROSC_BASE + ROSC_RANDOMBIT_OFFSET);
    
    for(k=0;k<nr_bits;k++){
        random = random << 1;
        random=random + (0x00000001 & (*rnd_reg));
    }
    return random;
}

uint32_t rnd_whitened(int nr_bits){
    int k, random=0;
    int random_bit1, random_bit2;
    volatile uint32_t *rnd_reg=(uint32_t *)(ROSC_BASE + ROSC_RANDOMBIT_OFFSET);
    
    for(k=0;k<nr_bits;k++){
        while(1){
            random_bit1=0x00000001 & (*rnd_reg);
            random_bit2=0x00000001 & (*rnd_reg);
            if(random_bit1!=random_bit2) break;
        }

	random = random << 1;        
        random=random + random_bit1;

    }
    return random;
}

float frnd(float min, float max)
{
    float r = ((float)(rnd() & 65535)/65536.0) * (max-min) + min;

    return r;
}

float distance_plane_point(t_plane plane, t_vec point)
{
    float d;

    d = vec_dot_vec(plane.normal, vec_sub_vec(point, plane.point));

    return d;
}

int calc_phys_led_nr(int virt_led_nr)
{
    // - determine the virtual triangle number (LED nr/21)
    // - look up the physical triangle (remap table)
    // - apply triangle rotation
    // - look up the physical LED number
    int virtual_triangle = virt_led_nr/21;
    int physical_triangle = remap_triangle[virtual_triangle];
    int virtual_led = virt_led_nr % 21;
    int physical_led = remap_led[rotate_triangle[virtual_triangle]][virtual_led]-1;
    int led_nr = physical_triangle * 21 + physical_led;

    return led_nr;
}

