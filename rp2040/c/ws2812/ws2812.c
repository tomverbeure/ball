/**
 * Copyright (c) 2020 Raspberry Pi (Trading) Ltd.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 */

#include <stdio.h>
#include <stdlib.h>

#include "pico/stdlib.h"
#include "hardware/pio.h"
#include "hardware/clocks.h"
#include "ws2812.pio.h"

typedef struct s_led_coord {
    float x;
    float y;
    float z;
} t_led_coord;

int remap_triangle[20] = {
    0, 6, 4, 7, 3, 8, 2, 9, 1, 5,   10, 11, 12, 13, 14,  17, 18, 19 , 15, 16
};

#include "led_coords.h"

#define IS_RGBW false
#define NUM_PIXELS 420

#ifdef PICO_DEFAULT_WS2812_PIN
#define WS2812_PIN PICO_DEFAULT_WS2812_PIN
#else
// default to pin 2 if the board doesn't have a default WS2812 pin defined
#define WS2812_PIN 0
#endif

static inline uint32_t urgb_u32(uint8_t r, uint8_t g, uint8_t b) {
    return
            ((uint32_t) (r) << 16) |
            ((uint32_t) (g) << 8) |
             (uint32_t) (b);
}

static inline void put_pixel(uint32_t pixel_rgb) {
    uint32_t r = (pixel_rgb >> 16) & 255;
    uint32_t g = (pixel_rgb >> 8)  & 255;
    uint32_t b =  pixel_rgb        & 255;

    const uint32_t max_val = 25;

    r = (r * max_val) / 256;
    g = (g * max_val) / 256;
    b = (b * max_val) / 256;

    pixel_rgb = urgb_u32(r,g,b);

    pio_sm_put_blocking(pio0, 0, pixel_rgb << 8u);
}

void pattern_snakes(uint len, uint t) {
    for (uint i = 0; i < len; ++i) {
        uint x = (i + (t >> 1)) % 64;
        if (x < 10)
            put_pixel(urgb_u32(0xff, 0, 0));
        else if (x >= 15 && x < 25)
            put_pixel(urgb_u32(0, 0xff, 0));
        else if (x >= 30 && x < 40)
            put_pixel(urgb_u32(0, 0, 0xff));
        else
            put_pixel(0);
    }
}

void pattern_one_by_one(uint len, uint t) {
    if (t % 4)
        return;
    for (int i = 0; i < len; ++i)
        if (i < t/4)
            put_pixel(0xffffff);
        else
            put_pixel(0x0);
}

void pattern_random(uint len, uint t) {
    if (t % 8)
        return;
    for (int i = 0; i < len; ++i)
        put_pixel(rand());
}

void pattern_sparkle(uint len, uint t) {
    if (t % 8)
        return;
    for (int i = 0; i < len; ++i)
        put_pixel(rand() % 16 ? 0 : 0xffffffff);
}

void pattern_greys(uint len, uint t) {
    int max = 100; // let's not draw too much current!
    t %= max;
    for (int i = 0; i < len; ++i) {
        put_pixel(t * 0x10101);
        if (++t >= max) t = 0;
    }
}

void pattern_gradient(uint len, uint t)
{
    for(int i = 0; i < len; ++i){
        const t_led_coord *c = &led_coords[i];

        uint8_t r,g,b; 

        r = (c->x + 1.0)/2 * 256;
        g = (c->y + 1.0)/2 * 256;
        b = (c->z + 1.0)/2 * 256;

        put_pixel(urgb_u32(r,g,b));
    }
}

void pattern_gradient_x(uint len, float t)
{
    for(int i = 0; i < len; ++i){
        const t_led_coord *c = &led_coords[i];

        uint8_t r,g,b; 

        r = (c->x <= t) ? 255 : 0;
        g = 0;
        b = 0;

        put_pixel(urgb_u32(r,g,b));
    }
}

void pattern_gradient_y(uint len, uint t)
{
    for(int i = 0; i < len; ++i){
        const t_led_coord *c = &led_coords[i];

        uint8_t r,g,b; 

        r = 0;
        g = (c->y + 1.0)/2 * 256;
        b = 0;

        put_pixel(urgb_u32(r,g,b));
    }
}

void pattern_gradient_z(uint len, uint t)
{
    for(int i = 0; i < len; ++i){
        const t_led_coord *c = &led_coords[i];

        uint8_t r,g,b; 

        r = 0;
        g = 0;
        b = (c->z + 1.0)/2 * 256;

        put_pixel(urgb_u32(r,g,b));
    }
}

void pattern_triangle_order(uint len, uint t)
{
    int tt = remap_triangle[t];

    for(int i = 0; i < len; ++i){
        int ct = i/21;          // current triangle
        if (ct == tt){
            put_pixel(urgb_u32(255, 0, 0));
        }
        else{
            put_pixel(urgb_u32(0, 0, 0));
        }
    }
}

void pattern_vertical_band(uint len, uint t)
{
    int bands[5][4]= {
        { 10, 9, 0, 15}, 
        { 11, 1, 2, 16}, 
        { 12, 3, 4, 17}, 
        { 13, 5, 6, 18}, 
        { 14, 7, 8, 19} 
    };
    

    int tt = remap_triangle[t];

    for(int i = 0; i < len; ++i){
        int ct = i/21;          // current triangle

        bool active = false;
        for(int j=0;j<4;++j){
            active = active |(ct == remap_triangle[bands[t][j]]);
        }

        if (active){
            put_pixel(urgb_u32(255, 0, 0));
        }
        else{
            put_pixel(urgb_u32(0, 0, 0));
        }
    }
}

typedef void (*pattern)(uint len, uint t);
const struct {
    pattern pat;
    const char *name;
} pattern_table[] = {
        {pattern_gradient,  "Gradient"},
//        {pattern_one_by_one,  "One by One"},
//        {pattern_snakes,  "Snakes!"},
//        {pattern_random,  "Random data"},
//        {pattern_sparkle, "Sparkles"},
//        {pattern_greys,   "Greys"},
};

int main() {
    stdio_init_all();
    printf("WS2812 Smoke Test, using pin %d", WS2812_PIN);

    // todo get free sm
    PIO pio = pio0;
    int sm = 0;
    uint offset = pio_add_program(pio, &ws2812_program);

    ws2812_program_init(pio, sm, offset, WS2812_PIN, 800000, IS_RGBW);

    int t = 0;
#if 0
    while (1) {
        int pat = rand() % count_of(pattern_table);
        //int dir = (rand() >> 30) & 1 ? 1 : -1;
        int dir = 1;
        puts(pattern_table[pat].name);
        puts(dir == 1 ? "(forward)" : "(backward)");
        for (int i = 0; i < 1000; ++i) {
            pattern_table[pat].pat(NUM_PIXELS, t);
            sleep_ms(10);
            t += dir;
        }
    }
#endif
#if 0
    while (1) {
        for(int i=0; i<NUM_PIXELS*4;++i){
            pattern_one_by_one(NUM_PIXELS, i);
            sleep_ms(10);
        }
    }
#endif
#if 0
    while(1){
        for(float t=-1.0;t<1.0;t+=0.05){
            pattern_gradient_x(NUM_PIXELS, t);
            sleep_ms(250); 
        }
    }
#endif
#if 0
    while(1){
        for(int t=0;t<20;++t){
            pattern_triangle_order(NUM_PIXELS, t);
            sleep_ms(400); 
        }
    }
#endif
#if 1
    while(1){
        for(int t=0;t<5;++t){
            pattern_vertical_band(NUM_PIXELS, t);
            sleep_ms(1000); 
        }
    }
#endif
}
