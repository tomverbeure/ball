#ifndef LIB_H
#define LIB_H

#include <stdint.h>
#include <math.h>
#include "hardware/pio.h"

#include "general.h"

uint32_t rnd(int nr_bits=32);
uint32_t rnd_whitened(int nr_bits=32);
float frnd(float min, float max);

static inline t_vec vec_plus_vec(t_vec v1, t_vec v2)
{
    t_vec v;

    v.x = v1.x + v2.x;
    v.y = v1.y + v2.y;
    v.z = v1.z + v2.z;

    return v;
}

static inline t_vec vec_sub_vec(t_vec v1, t_vec v2)
{
    t_vec v;

    v.x = v1.x - v2.x;
    v.y = v1.y - v2.y;
    v.z = v1.z - v2.z;

    return v;
}

static inline float vec_dot_vec(t_vec v1, t_vec v2)
{
    float dot;

    dot = v1.x * v2.x + v1.y * v2.y + v1.z * v2.z;

    return dot;
}

static inline t_vec vec_mul_scalar(t_vec v1, float s)
{
    t_vec v;

    v.x = v1.x * s;
    v.y = v1.y * s;
    v.z = v1.z * s;

    return v;
}

static inline t_vec vec_normalize(t_vec v)
{
    float d = sqrtf(vec_dot_vec(v, v)); 
    
    t_vec n = vec_mul_scalar(v, 1/d);

    return n;
}

float distance_plane_point(t_plane plane, t_vec point);

void rotation_matrix(t_matrix3D m, float x, float y, float z);
t_vec matrix_mul_vec(t_matrix3D m, const t_vec &v);

static inline uint32_t urgb_u32(uint8_t r, uint8_t g, uint8_t b) {
    return
            ((uint32_t) (r) << 16) |
            ((uint32_t) (g) << 8) |
             (uint32_t) (b);
}

inline void put_pixel(const t_color &c)
{
    uint8_t r = (uint16_t)c.r * max_value / 256;
    uint8_t g = (uint16_t)c.g * max_value / 256;
    uint8_t b = (uint16_t)c.b * max_value / 256;

    uint32_t pixel_rgb = urgb_u32(r,g,b);
    pio_sm_put_blocking(pio0, 0, pixel_rgb << 8u);
}

void init_remap();
int calc_phys_led_nr(int virt_led_nr);

#endif
