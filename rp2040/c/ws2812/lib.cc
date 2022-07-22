#include "lib.h"

#include <stdio.h>

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

void init_remap()
{
    for(int virt = 0; virt < NUM_PIXELS; ++virt){
        int phys = calc_phys_led_nr(virt);
        remap_led_phys_to_virt[phys] = virt;
    }
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
    int physical_led = remap_triangle_led[rotate_triangle[virtual_triangle]][virtual_led]-1;
    int led_nr = physical_triangle * 21 + physical_led;

    return led_nr;
}

void rotation_matrix(t_matrix3D m, float x, float y, float z)
{
    float cos_a = cosf(x);
    float cos_b = cosf(y);
    float cos_g = cosf(z);

    float sin_a = sinf(x);
    float sin_b = sinf(y);
    float sin_g = sinf(z);
    
    m[0][0] = cos_b * cos_g;
    m[0][1] = sin_a * sin_b * cos_g - cos_a * sin_g;
    m[0][2] = cos_a * sin_b * cos_g + sin_a * sin_g;

    m[1][0] = cos_b * sin_g;
    m[1][1] = sin_a * sin_b * sin_g + cos_a * cos_g;
    m[1][2] = cos_a * sin_b * sin_g - sin_a * cos_g;

    m[2][0] = -sin_b;
    m[2][1] = sin_a * cos_b;
    m[2][2] = cos_a * cos_b;

    for(int y=0;y<3;++y){
        for(int x=0;x<3;++x){
            printf("%f ", m[y][x]);
        }
            printf("\n");
    }
}

t_vec matrix_mul_vec(t_matrix3D m, const t_vec &v)
{
    t_vec r;

    r.x = m[0][0] * v.x + m[0][1] * v.y + m[0][2] * v.z;
    r.y = m[1][0] * v.x + m[1][1] * v.y + m[1][2] * v.z;
    r.z = m[2][0] * v.x + m[2][1] * v.y + m[2][2] * v.z;

    return r;
}



