#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "pico/stdlib.h"
#include "hardware/pio.h"
#include "hardware/i2c.h"
#include "hardware/clocks.h"
#include "ws2812.pio.h"

#include "general.h"
#include "lib.h"

#include "particles.h"

#define IS_RGBW false

const int max_value = 30;

const t_color black   = { 0,0,0 };
const t_color white   = { 255,255,255 };
const t_color red     = { 255,0,0 };
const t_color green   = { 0,255,0 };
const t_color blue    = { 0,0,255 };
const t_color cyan    = { 0,255,255 };
const t_color yellow  = { 255,255,255 };
const t_color orange  = { 255,165,0 };
const t_color purple  = { 0xa0,0x20,0xf0 };


// Maps the triangle order of the FreeCAD model (and thus the LED coordinates)
// to the way the triangles have been physically wired together.
const int8_t remap_triangle[20] = {
    5, 6, 7, 8, 9,  0, 4, 3, 2, 1, 10, 11, 12, 13, 14,  16, 15, 19, 18, 17
};

const int8_t rotate_triangle[20] = { 
    0, 0, 0, 0, 0,  0, 0, 0, 0, 0,  2, 2, 2, 2, 1,  1, 1, 1, 1, 1
};

// The FreeCAD model has the LEDs in scan order. The PCB has them
// going from center to outside. So remap them from scan order to
// PCB order. The numbers are the LED numbers on the PCB, so it
// starts with 1!
const int8_t remap_led[3][21] = {
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



static inline void put_pixel(uint32_t pixel_rgb) {
    uint32_t r = (pixel_rgb >> 16) & 255;
    uint32_t g = (pixel_rgb >> 8)  & 255;
    uint32_t b =  pixel_rgb        & 255;

    r = (r * max_value) / 256;
    g = (g * max_value) / 256;
    b = (b * max_value) / 256;

    pixel_rgb = urgb_u32(r,g,b);

    pio_sm_put_blocking(pio0, 0, pixel_rgb << 8u);
}

void send_buffer(t_color led_buffer[NUM_PIXELS])
{
    for(int i=0; i<NUM_PIXELS;++i){
        put_pixel(led_buffer[i]);
    }   
}

void pattern_fixed_color(t_color led_buffer[NUM_PIXELS], const t_color &c) {
    for(int i=0;i<NUM_PIXELS;++i){
        led_buffer[i] = c;
    }
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

void pattern_rings(
            t_color led_buffer[NUM_PIXELS], 
            float offset, 
            float ring_thickness, 
            t_vec start, 
            t_vec dir, 
            t_color col, 
            int nr_rings=1,
            float spacing_thickness=0.0)
{
#if 0
    // For debug only...
    for(int i = 0; i < NUM_PIXELS; ++i){
        led_buffer[i] = blue;
    }
#endif

    t_plane     plane;
    plane.point     = vec_plus_vec(start, vec_mul_scalar(dir, offset));
    plane.normal    = vec_normalize(dir);

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
            c = d < ring_thickness ? col : black;
        }

        led_buffer[calc_phys_led_nr(i)] = c;
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

int reg_read(  i2c_inst_t *i2c,
                const uint addr,
                const uint8_t reg,
                uint8_t *buf,
                const uint8_t nbytes) {

    int num_bytes_read = 0;

    // Check to make sure caller is asking for 1 or more bytes
    if (nbytes < 1) {
        return 0;
    }

    // Read data from register(s) over I2C
    i2c_write_blocking(i2c, addr, &reg, 1, true);
    num_bytes_read = i2c_read_blocking(i2c, addr, buf, nbytes, false);

    return num_bytes_read;
}

int main() {
    stdio_init_all();
    printf("WS2812 Smoke Test, using pin %d", WS2812_PIN);

    // Config WS2812 PIO
    PIO pio = pio0;
    int sm = 0;
    uint offset = pio_add_program(pio, &ws2812_program);

    ws2812_program_init(pio, sm, offset, WS2812_PIN, 800000, IS_RGBW);

    // Config I2C port
    const uint sda_pin = 20; 
    const uint scl_pin = 21; 

    i2c_inst_t *i2c = i2c0;
    i2c_init(i2c, 400 * 1000);
    gpio_set_function(sda_pin, GPIO_FUNC_I2C);
    gpio_set_function(scl_pin, GPIO_FUNC_I2C);

    int t = 0;

    t_color led_buffer[NUM_PIXELS];

    // Cleanup lingering colors...
    pattern_fixed_color(led_buffer, black);
    send_buffer(led_buffer);

#if 0
    // Ring back and forth for each axis.
    {
        t_vec starts[6] = { 
                { -1.0,  0.0,  0.0 },
                {  1.0,  0.0,  0.0 },
                {  0.0, -1.0,  0.0 },
                {  0.0,  1.0,  0.0 },
                {  0.0,  0.0, -1.0 },
                {  0.0,  0.0,  1.0 } };
        t_color cols[6] = { red, red, green, green, blue, blue };

        for(int i=0;i<6;++i){
            t_vec start = starts[i];
            t_vec dir = vec_mul_scalar(start, -1);
            int   nr_rings      = 3;
            float ring_thickness = 0.15;
            float spacing_thickness = 0.4;
            float total_thickness = (nr_rings * ring_thickness) + ((nr_rings-1) * spacing_thickness);
        
            for(float l=-total_thickness;l<2;l+=0.08){
                pattern_rings(led_buffer, l, ring_thickness, start, dir, cols[i], nr_rings, spacing_thickness);
                send_buffer(led_buffer);
            }
        }
    }
#endif

#if 1
    Particles p;

    p.init();
    p.render(led_buffer);
    send_buffer(led_buffer);

    t_vec dir = { -1.0, -0.5, -0.5 };
    dir = vec_normalize(dir);

    while(1){
        sleep_ms(1000);
        for(int i=0;i<50;++i){
            p.calc_next_frame(dir);
            p.render(led_buffer);
            send_buffer(led_buffer);
            sleep_ms(1);
        }
        dir = vec_mul_scalar(dir,-1.0);
    }
#endif

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
        for(float t=-1.05;t<1.05;t+=0.04){
            pattern_gradient(t);
            //sleep_ms(2); 
        }
    }
#endif
#if 1
    while(1){
        {
            printf("*");
            t_vec   start;
            t_vec   dir;
            t_color color = { (uint8_t)rnd(), (uint8_t)rnd(), (uint8_t)rnd() };
    
            start.x = frnd(-1.0, 1.0);
            start.y = frnd(-1.0, 1.0);
            start.z = frnd(-1.0, 1.0);
            start = vec_normalize(start);
            dir = vec_mul_scalar(start, -1.0);
            float ring_thickness = frnd(0.1, 1.0);
            float spacing_thickness = frnd(0.3, 0.5);
            int nr_rings = (rnd() % 2)+1;
            float total_thickness = (nr_rings * ring_thickness) + ((nr_rings-1) * spacing_thickness);

            float speed = frnd(0.06, 0.15);

            for(float l=-total_thickness;l<2;l+=speed){
                pattern_rings(led_buffer, l, ring_thickness, start, dir, color, nr_rings, spacing_thickness);
                send_buffer(led_buffer);
            }
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
