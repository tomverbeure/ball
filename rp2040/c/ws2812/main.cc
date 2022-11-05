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
#include "mpu6050_drv.h"

#include "particles.h"
#include "rings.h"
#include "random_rings.h"
#include "startup_rings.h"
#include "pride_flag.h"
#include "sparkles.h"
#include "rgb_sphere.h"

#define IS_RGBW false

#define STARTUP_EFFECT          1
#define RGB_SPHERE_EFFECT       0
#define SPARKLES_EFFECT         1
#define PRIDE_FLAG_EFFECT       1
#define RANDOM_RINGS_EFFECT     1

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
const int8_t remap_triangle_led[3][21] = {
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

// Lookup table that maps the location of all physical LEDs to its
// virtual location in the chain.
// This table is necessary if we want to send the LEDs in 
// physical order to the chain while doing a lookup in the virtual
// buffer.
int16_t remap_led_phys_to_virt[NUM_PIXELS];

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

void send_virtual_buffer(t_color led_buffer[NUM_PIXELS])
{
    for(int i=0; i<NUM_PIXELS;++i){
        put_pixel(led_buffer[remap_led_phys_to_virt[i]]);
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

void pattern_triangle_order(uint len, uint t)
{
    int8_t tt = remap_triangle[t];

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

typedef void (*pattern)(uint len, uint t);
const struct {
    pattern pat;
    const char *name;
} pattern_table[] = {
//        {pattern_gradient,  "Gradient"},
//        {pattern_one_by_one,  "One by One"},
//        {pattern_snakes,  "Snakes!"},
//        {pattern_random,  "Random data"},
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

#if 0
    // setup blink led
    gpio_init(PICO_DEFAULT_LED_PIN);
    gpio_set_dir(PICO_DEFAULT_LED_PIN, GPIO_OUT);
    while (!stdio_usb_connected()) { // blink the pico's led until usb connection is established
        gpio_put(PICO_DEFAULT_LED_PIN, 1);
        sleep_ms(250);
        gpio_put(PICO_DEFAULT_LED_PIN, 0);
        sleep_ms(250);
    }
#endif

    printf("WS2812 Smoke Test, using pin %d", WS2812_PIN);

    init_remap();

    // Config WS2812 PIO
    PIO pio = pio0;
    int sm = 0;
    uint offset = pio_add_program(pio, &ws2812_program);

    ws2812_program_init(pio, sm, offset, WS2812_PIN, 800000, IS_RGBW);

#if 0
    mpu6050_init();
    mpu6050_gravity();
#endif

    int t = 0;

    t_color led_buffer[NUM_PIXELS];

    // Cleanup lingering colors...
    pattern_fixed_color(led_buffer, black);
    send_buffer(led_buffer);

    while(1){
#if STARTUP_EFFECT==1
        // Ring back and forth for each axis.
        {
            StartupRings startup_rings;
            startup_rings.init();

            bool done;
            do {
                done = startup_rings.calc_next_frame();
                startup_rings.render(led_buffer);
                send_virtual_buffer(led_buffer);
            } while(!done);
        }
#endif
#if RGB_SPHERE_EFFECT==1
        {
            RGBSphere rgb_sphere;
            rgb_sphere.init();

            for(int i=0;i<10;++i){
                for(float offset=-M_PI; offset<M_PI;offset+=0.12){
                    rgb_sphere.calc_next_frame(offset);
                    rgb_sphere.render(led_buffer);
                    send_virtual_buffer(led_buffer);
                    sleep_ms(5);
                }
            }
        }
#endif
#if SPARKLES_EFFECT==1
        {
            Sparkles sparkles;
            sparkles.init();

            for(int i=0;i<100;++i){
                sparkles.calc_next_frame(0.0);
                sparkles.render(led_buffer);
                send_virtual_buffer(led_buffer);
                sleep_ms(20);
            }
        }
#endif
#if PRIDE_FLAG_EFFECT==1
        {
            PrideFlag pride_flag;
            pride_flag.init();

            for(float offset=0.0; offset<50;offset+=0.1){
                pride_flag.calc_next_frame(offset);
                pride_flag.render(led_buffer);
                send_virtual_buffer(led_buffer);
                sleep_ms(5);
            }
        }
#endif
#if RANDOM_RINGS_EFFECT==1
        {
            RandomRings random_rings;
            for(int i=0; i<20;++i){
                random_rings.init();

                bool done;
                do {
                    done = random_rings.calc_next_frame();
                    random_rings.render(led_buffer);
                    send_virtual_buffer(led_buffer);
                } while(!done);
            }
        }
#endif
    }



#if 0
    Particles p;

    p.init();
    p.render(led_buffer);
    send_buffer(led_buffer);

    //t_vec dir = { -1.0, -0.5, -0.5 };
    t_vec dir = mpu6050_gravity();

    while(1){
        //sleep_ms(1000);
        for(int i=0;i<50;++i){
            dir = mpu6050_gravity();
            dir = vec_mul_scalar(dir, -1.0);
            p.calc_next_frame(dir);
            p.render(led_buffer);
            send_buffer(led_buffer);
        }
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
#if 0
    while(1){
        for(int t=0;t<20;++t){
            pattern_triangle_order(NUM_PIXELS, t);
            sleep_ms(1000); 
        }
    }
#endif
}
