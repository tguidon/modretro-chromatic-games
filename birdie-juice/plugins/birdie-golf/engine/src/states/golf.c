#pragma bank 255
#include <string.h>
#include "states/golf.h"
#include "states/birdie_direction.h"
#include "actor.h"
#include "camera.h"
#include "data_manager.h"
#include "game_time.h"
#include "input.h"
#include "ui.h"
#include "vm.h"
#include "math.h"
#include "macro.h"
#include "data/scene_hole_01.h"
#include "data/scene_hole_02.h"
#include "data/scene_hole_03.h"
#include "data/scene_hole_04.h"
#include "data/scene_hole_05.h"
#include "data/scene_hole_06.h"
#include "data/scene_hole_07.h"
#include "data/scene_hole_08.h"
#include "data/scene_hole_09.h"

UBYTE bj_hole, bj_club, bj_power, bj_angle, bj_strokes, bj_mode;
UBYTE bj_scores[9], bj_notice, bj_help_return;
UWORD bj_total;
INT16 bj_x, bj_y;
bj_hole_t bj_course;
static INT16 bj_from_x, bj_from_y;
static UBYTE bj_repeat, bj_hud_tick, bj_wait, bj_swing_tick, bj_meter_back;
INT16 bj_meter, bj_accuracy;

static void bj_sound(UBYTE tone) {
    NR52_REG=0x80; NR50_REG=0x77; NR51_REG=0xFF;
    NR21_REG=0x80; NR22_REG=0x82; NR23_REG=tone; NR24_REG=0x86;
}
static UBYTE bj_distance_to_cup(void) {
    INT16 dx=(bj_x>>4)-bj_course.cup_x, dy=(bj_y>>4)-bj_course.cup_y;
    // Manhattan distance is only used to choose a suitable club, never for capture.
    if(dx<0)dx=-dx; if(dy<0)dy=-dy;
    return (UBYTE)(dx+dy);
}
static void bj_auto_aim(void) {
    UBYTE i,best=0;
    INT16 dx=bj_course.cup_x-(bj_x>>4),dy=bj_course.cup_y-(bj_y>>4);
    INT32 dot,best_dot=-2147483647L;
    for(i=0;i<64;i++) {
        dot=(INT32)dx*bj_cos[i]+(INT32)dy*bj_sin[i];
        if(dot>best_dot) {best_dot=dot;best=i;}
    }
    bj_angle=best;
}
static void bj_place_actors(UBYTE height) {
    INT16 mx,my;
    if(bj_mode!=BJ_AIM && bj_mode!=BJ_FLIGHT) {
        SET_FLAG(PLAYER.flags,ACTOR_FLAG_HIDDEN);
        SET_FLAG(actors[1].flags,ACTOR_FLAG_HIDDEN);
        SET_FLAG(actors[2].flags,ACTOR_FLAG_HIDDEN);
        SET_FLAG(actors[3].flags,ACTOR_FLAG_HIDDEN);
        SET_FLAG(actors[4].flags,ACTOR_FLAG_HIDDEN);
        return;
    }
    SET_FLAG(actors[4].flags,ACTOR_FLAG_HIDDEN);
    CLR_FLAG(actors[2].flags,ACTOR_FLAG_HIDDEN);
    CLR_FLAG(actors[3].flags,ACTOR_FLAG_HIDDEN);
    actor_set_frame_offset(&actors[3],(game_time>>4)&1);
    PLAYER.pos.x=(UWORD)((bj_x-128)*2);
    PLAYER.pos.y=(UWORD)((bj_y-((INT16)height<<4))*2);
    CLR_FLAG(PLAYER.flags,ACTOR_FLAG_HIDDEN|ACTOR_FLAG_COLLISION);
    if(bj_mode==BJ_AIM) {
        mx=bj_target_x;my=bj_target_y;
        actor_set_frame_offset(&actors[1],bj_spread>4?1:0);
        if(mx>=8 && mx<152 && my>=20 && my<125) {
            actors[1].pos.x=(UWORD)((mx-8)*32);
            actors[1].pos.y=(UWORD)(my*32);
            CLR_FLAG(actors[1].flags,ACTOR_FLAG_HIDDEN);
        } else SET_FLAG(actors[1].flags,ACTOR_FLAG_HIDDEN);
    } else {
        SET_FLAG(actors[1].flags,ACTOR_FLAG_HIDDEN);
        actors[4].pos.x=(UWORD)((bj_x-128)*2);
        actors[4].pos.y=(UWORD)(bj_y*2);
        CLR_FLAG(actors[4].flags,ACTOR_FLAG_HIDDEN);
    }
    if(bj_mode!=BJ_FLIGHT) {
        // The golfer moves to the next lie between strokes.
        mx=(bj_x>>4)-19; if(mx<0)mx=0;
        actors[2].pos.x=(UWORD)(mx*32);
        actors[2].pos.y=(UWORD)((bj_y>>4)*32);
    }
}
static void bj_finish_hole(void) {
    bj_z=0;
    bj_x=(INT16)bj_course.cup_x<<4; bj_y=(INT16)bj_course.cup_y<<4;
    bj_scores[bj_hole]=bj_strokes;
    bj_mode=BJ_HOLED; bj_wait=24;
    bj_sound(220);
    if(bj_hole==8) {bj_help_return=BJ_HOLED;bj_mode=BJ_CARD;}
    bj_draw_panel();
}
static void bj_settle(void) {
    UBYTE lie=bj_terrain(bj_hole,(UBYTE)(bj_x>>4),(UBYTE)(bj_y>>4));
    if(lie==BJ_WATER) {
        bj_x=bj_from_x;bj_y=bj_from_y;
        bj_strokes++;bj_total++;bj_notice=1;bj_sound(45);
    } else if(lie==BJ_TREE) {
        bj_x=bj_from_x;bj_y=bj_from_y;bj_notice=2;bj_sound(60);
    }
    if(bj_strokes>=12) {
        bj_total-=bj_strokes-12;bj_strokes=12;
        bj_notice=3;bj_finish_hole();return;
    }
    bj_mode=BJ_AIM;bj_auto_aim();
    bj_wind_x=bj_course.wind_x;bj_wind_y=bj_course.wind_y;
    lie=bj_terrain(bj_hole,(UBYTE)(bj_x>>4),(UBYTE)(bj_y>>4));
    if(lie==BJ_GREEN || bj_distance_to_cup()<=16) bj_club=4;
    bj_draw_hud();
}
static void bj_swing(void) {
    bj_from_x=bj_x;bj_from_y=bj_y;
    bj_physics_start();
    bj_mode=BJ_FLIGHT;bj_strokes++;bj_total++;
    bj_notice=(bj_accuracy>=-3 && bj_accuracy<=3)?4:5;
    bj_close_panel();bj_sound(bj_notice==4?220:100);bj_draw_hud();
}
static void bj_lock_accuracy(void) {
    bj_accuracy=bj_meter-10;
    bj_mode=BJ_SWING;bj_swing_tick=0;
    bj_shot_pose(1);bj_shot_meter();
}
static void bj_next(void) {
    // The aim actor owns an ordinary editable GB Studio scene-transition event.
    if(actors[1].script.bank) {
        bj_wait=255;
        script_execute(actors[1].script.bank,actors[1].script.ptr,0,0);
    }
}
void golf_init(void) BANKED {
    bj_hole=0;
    if(current_scene.ptr==&scene_hole_02 && current_scene.bank==BANK(scene_hole_02))bj_hole=1;
    else if(current_scene.ptr==&scene_hole_03 && current_scene.bank==BANK(scene_hole_03))bj_hole=2;
    else if(current_scene.ptr==&scene_hole_04 && current_scene.bank==BANK(scene_hole_04))bj_hole=3;
    else if(current_scene.ptr==&scene_hole_05 && current_scene.bank==BANK(scene_hole_05))bj_hole=4;
    else if(current_scene.ptr==&scene_hole_06 && current_scene.bank==BANK(scene_hole_06))bj_hole=5;
    else if(current_scene.ptr==&scene_hole_07 && current_scene.bank==BANK(scene_hole_07))bj_hole=6;
    else if(current_scene.ptr==&scene_hole_08 && current_scene.bank==BANK(scene_hole_08))bj_hole=7;
    else if(current_scene.ptr==&scene_hole_09 && current_scene.bank==BANK(scene_hole_09))bj_hole=8;
    if(!bj_hole) {memset(bj_scores,0,sizeof(bj_scores));bj_total=0;}
    bj_read_hole(bj_hole,&bj_course);
    bj_x=(INT16)bj_course.tee_x<<4;bj_y=(INT16)bj_course.tee_y<<4;
    bj_strokes=0;bj_club=0;bj_power=100;bj_notice=0;bj_repeat=0;bj_wait=16;bj_hud_tick=0;
    bj_mode=bj_hole?BJ_AIM:BJ_TITLE;
    bj_meter=0;bj_accuracy=0;bj_z=0;bj_wind_x=bj_course.wind_x;bj_wind_y=bj_course.wind_y;
    camera_offset_x=0;camera_offset_y=0;camera_deadzone_x=0;camera_deadzone_y=0;
    bj_load_font();bj_auto_aim();bj_predict();
    actors[3].pos.x=(bj_course.cup_x-8)*32;
    actors[3].pos.y=(bj_course.cup_y-3)*32;
    bj_place_actors(0);
    bj_close_panel();
    if(bj_mode==BJ_TITLE)bj_draw_panel();
}
void golf_update(void) BANKED {
    UBYTE pressed=joy_pressed, height=0;
    if(bj_wait && bj_wait!=255)bj_wait--;
    if(bj_hud_tick<2) {bj_hud_tick++;bj_draw_hud();}
    if(bj_mode==BJ_TITLE) {
        if(!bj_wait && (pressed&J_A)) {bj_mode=BJ_AIM;bj_close_panel();bj_sound(180);bj_draw_hud();}
        else if(pressed&J_START) {bj_help_return=BJ_TITLE;bj_mode=BJ_HELP;bj_draw_panel();}
    } else if(bj_mode==BJ_HELP) {
        if(pressed&(J_A|J_B|J_START)) {bj_mode=bj_help_return;if(bj_mode==BJ_AIM)bj_close_panel();else bj_draw_panel();}
    } else if(bj_mode==BJ_CARD) {
        if(!bj_wait && (pressed&J_A) && bj_hole==8 && bj_scores[8])bj_next();
        else if(pressed&(J_B|J_START|J_A)) {bj_mode=bj_help_return;if(bj_mode==BJ_AIM)bj_close_panel();else bj_draw_panel();}
    } else if(bj_mode==BJ_HOLED) {
        if(!bj_wait && (pressed&J_A))bj_next();
        else if(pressed&J_START) {bj_help_return=BJ_HOLED;bj_mode=BJ_CARD;bj_draw_panel();}
    } else if(bj_mode==BJ_POWER) {
        if(pressed&J_B) {bj_mode=BJ_AIM;bj_close_panel();bj_draw_hud();}
        else if(pressed&J_A) {
            bj_power=bj_meter<5?5:bj_meter;
            bj_mode=BJ_ACCURACY;bj_meter=100;bj_shot_pose(1);bj_shot_meter();bj_sound(150);
        } else {
            if(bj_meter_back) {bj_meter-=2;if(bj_meter<=0)bj_meter_back=0;}
            else {bj_meter+=2;if(bj_meter>=100)bj_meter_back=1;}
            if(bj_meter==24)bj_shot_pose(4);
            if(bj_meter==50)bj_shot_pose(5);
            if(bj_meter==76)bj_shot_pose(1);
            bj_shot_meter();
        }
    } else if(bj_mode==BJ_ACCURACY) {
        if((pressed&J_A) || bj_meter<=-10)bj_lock_accuracy();
        else {bj_meter-=2;bj_shot_meter();}
    } else if(bj_mode==BJ_SWING) {
        bj_swing_tick++;
        if(bj_swing_tick==4)bj_shot_pose(4);
        if(bj_swing_tick==8) {bj_shot_pose(2);bj_sound(bj_accuracy>=-3 && bj_accuracy<=3?235:90);}
        if(bj_swing_tick==16)bj_shot_pose(3);
        if(bj_swing_tick>=30)bj_swing();
    } else if(bj_mode==BJ_FLIGHT) {
        UBYTE result=bj_physics_step();
        height=(UBYTE)(bj_z>>4);
        if(result==BJ_SUNK) {bj_finish_hole();height=0;}
        else if(result==BJ_SPLASH) {
            bj_x=bj_from_x;bj_y=bj_from_y;bj_strokes++;bj_total++;bj_notice=1;
            bj_sound(45);bj_settle();height=0;
        } else if(result==BJ_STOPPED) {bj_settle();height=0;}
    } else {
        if(pressed&J_START) {bj_help_return=BJ_AIM;bj_mode=BJ_CARD;bj_draw_panel();}
        else if(pressed&J_B) {bj_notice=0;bj_club=(bj_club+1)%5;bj_sound(130);bj_draw_hud();}
        else if(pressed&J_SELECT) {bj_notice=0;bj_club=(bj_club+4)%5;bj_sound(130);bj_draw_hud();}
        else if(pressed&J_A) {
            bj_mode=BJ_POWER;bj_meter=0;bj_meter_back=0;bj_accuracy=0;
            bj_shot_open();
        }
        else {
            if(!(joy&J_RIGHT) && !(joy&J_LEFT) && !(joy&J_UP) && !(joy&J_DOWN))bj_repeat=0;
            if(pressed&(J_RIGHT|J_LEFT|J_UP|J_DOWN))bj_repeat=0;
            if(!bj_repeat) {
                if(joy&J_RIGHT)bj_angle=(bj_angle+1)&63;
                else if(joy&J_LEFT)bj_angle=(bj_angle+63)&63;
                // Timed swings leave powers between five-percent steps.
                if((joy&J_UP) && bj_power<100)bj_power=bj_power>95?100:bj_power+5;
                else if((joy&J_DOWN) && bj_power>5)bj_power=bj_power<10?5:bj_power-5;
                if(joy&(J_RIGHT|J_LEFT|J_UP|J_DOWN)) {bj_notice=0;bj_repeat=6;bj_draw_hud();}
            } else bj_repeat--;
        }
    }
    bj_place_actors(height);
}
