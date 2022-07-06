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

// Maps the triangle order of the FreeCAD model (and thus the LED coordinates)
// to the way the triangles have been physically wired together.
int remap_triangle[20] = {
    5, 6, 7, 8, 9,  0, 4, 3, 2, 1, 10, 11, 12, 13, 14,  16, 15, 19, 18, 17
};

int rotate_triangle[20] = { 
    0, 0, 0, 0, 0,  0, 0, 0, 0, 0,  2, 2, 2, 2, 1,  1, 1, 1, 1, 1
};

// The FreeCAD model has the LEDs in scan order. The PCB has them
// going from center to outside. So remap them from scan order to
// PCB order. The numbers are the LED numbers on the PCB, so it
// starts with 1!
int remap_led[3][21] = {
    // LED 2 on top
    { 
    15, 16, 17, 18, 19, 20, 
    14, 5, 2, 6, 21,
    13, 1, 3, 7, 
    12, 4, 8, 
    11, 9, 
    10
    },
    // LED 1 on top
    { 
    10, 11, 12, 13, 14, 15,
    9,  4, 1, 5, 16,
    8, 3, 2, 17, 
    7, 6, 18,
    21, 19,
    20
    },
    // LED 3 on top
    { 
    20, 21, 7, 8, 9, 10,
    19, 6, 3, 4, 11,
    18, 2, 1, 12,
    17, 5, 13,
    16, 14,
    15
    }
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

void pattern_gradient(float t)
{
    // For each LED:
    // - look up the (x,y,z) coordinates
    // - calculate the value
    // - Store LED RGB value in physical LED array
    // - When all is done, send array to PIO

    uint32_t led_rgb_values[NUM_PIXELS];

    // Init dummy value...
    for(int i = 0; i < NUM_PIXELS; ++i){
        led_rgb_values[i] = 0xff;
    }

    for(int i = 0; i < NUM_PIXELS; ++i){
        const t_led_coord *c = &led_coords[i];

        uint8_t r,g,b; 

        r = 0;
        g = 0;
        b = 0;

        r = (c->x <= t) ? 255 : 0;
        g = (c->y <= t) ? 255 : 0;
        b = (c->z <= t) ? 255 : 0;

        led_rgb_values[calc_phys_led_nr(i)] = urgb_u32(r,g,b);
    }

    for(int i = 0; i < NUM_PIXELS; ++i){
        put_pixel(led_rgb_values[i]);
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
        { 10, 0, 5, 16}, 
        { 11, 1, 6, 17}, 
        { 12, 2, 7, 17}, 
        { 13, 3, 8, 18}, 
        { 14, 4, 9, 15} 
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
//        {pattern_gradient,  "Gradient"},
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
#if 1
    while(1){
        for(float t=-1.05;t<1.05;t+=0.04){
            pattern_gradient(t);
            //sleep_ms(2); 
        }
    }
#endif
#if 0
    while(1){
        for(int t=0;t<20;++t){
            pattern_triangle_order(NUM_PIXELS, t);
            sleep_ms(1000); 
        }
    }
#endif
#if 0
    while(1){
        for(int t=0;t<5;++t){
            pattern_vertical_band(NUM_PIXELS, t);
            sleep_ms(1000); 
        }
    }
#endif
}
