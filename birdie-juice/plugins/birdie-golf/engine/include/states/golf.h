#ifndef BIRDIE_GOLF_H
#define BIRDIE_GOLF_H
#include <gbdk/platform.h>
typedef struct bj_hole_t {
    UBYTE par, tee_x, tee_y, cup_x, cup_y;
    char name[17];
    INT8 wind_x, wind_y, slope_x, slope_y;
} bj_hole_t;
enum { BJ_AIM, BJ_FLIGHT, BJ_HOLED, BJ_CARD, BJ_TITLE, BJ_HELP, BJ_POWER, BJ_ACCURACY, BJ_SWING };
enum { BJ_ROUGH, BJ_FAIRWAY, BJ_GREEN, BJ_SAND, BJ_WATER, BJ_TREE };
extern UBYTE bj_hole, bj_club, bj_power, bj_angle, bj_strokes, bj_mode;
extern UBYTE bj_scores[9], bj_notice, bj_help_return;
extern UWORD bj_total;
extern INT16 bj_x, bj_y;
extern bj_hole_t bj_course;
extern INT16 bj_meter, bj_accuracy, bj_z, bj_vx, bj_vy;
extern INT8 bj_wind_x, bj_wind_y;
extern UBYTE bj_bounces, bj_roll_frames;
enum { BJ_MOVING, BJ_STOPPED, BJ_SPLASH, BJ_SUNK };
UBYTE bj_carry(void) BANKED;
void bj_physics_start(void) BANKED;
UBYTE bj_physics_step(void) BANKED;
void bj_shot_art(void) BANKED;
void bj_shot_pose(UBYTE pose) BANKED;
void bj_shot_open(void) BANKED;
void bj_shot_meter(void) BANKED;
void golf_init(void) BANKED;
void golf_update(void) BANKED;
void bj_read_hole(UBYTE hole, bj_hole_t *dest) BANKED;
UBYTE bj_terrain(UBYTE hole, UBYTE x, UBYTE y) BANKED;
void bj_load_font(void) BANKED;
void bj_draw_hud(void) BANKED;
void bj_draw_panel(void) BANKED;
void bj_close_panel(void) BANKED;
#endif
