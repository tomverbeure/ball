#ifndef GENERAL_H
#define GENERAL_H

#define NUM_PIXELS 420

typedef struct s_vec {
    float x;
    float y;
    float z;
} t_vec;

typedef struct s_plane {
    t_vec   point;
    t_vec   normal;
} t_plane;

typedef struct s_color {
    uint8_t r;
    uint8_t g;
    uint8_t b;
} t_color;

typedef struct s_vec t_led_coord;

extern const t_vec led_coords[420];
extern const uint16_t closest_leds[420][6];
extern const int8_t remap_triangle[20];
extern const int8_t rotate_triangle[20];
extern const int8_t remap_led[3][21];

extern const t_color black; 
extern const t_color white;
extern const t_color red;
extern const t_color green;
extern const t_color blue;
extern const t_color cyan;
extern const t_color yellow;
extern const t_color orange;
extern const t_color purple;

extern const int max_value;

#endif
