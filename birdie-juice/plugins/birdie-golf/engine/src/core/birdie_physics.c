#pragma bank 255
#include "states/golf.h"

// Position and horizontal speed use 8 fractional bits; altitude uses 4.
// Gravity, drag and slope acceleration are integrated every game update.
INT16 bj_z, bj_vx, bj_vy;
INT8 bj_wind_x, bj_wind_y;
UBYTE bj_bounces, bj_roll_frames;
static INT32 px,py;
static INT16 vz;
static UWORD age;
static UBYTE tree_cooldown, airborne;
static const UBYTE ranges[5]={54,45,33,22,22};
static const UBYTE loft[4]={44,50,56,64};

static INT16 magnitude(INT16 n) {return n<0?-n:n;}
UBYTE bj_carry(void) BANKED {
    UWORD distance=(UWORD)ranges[bj_club]*bj_power/100;
    UBYTE lie=bj_terrain(bj_hole,(UBYTE)(bj_x>>4),(UBYTE)(bj_y>>4));
    if(bj_club==4)distance=(UINT32)ranges[4]*bj_power*bj_power/10000;
    else if(bj_club!=3) {
        if(lie==BJ_SAND)distance=distance/2;
        else if(lie==BJ_ROUGH)distance=distance*3/4;
    }
    return distance?distance:1;
}
void bj_physics_start(void) BANKED {
    INT16 speed,error=bj_accuracy;
    UBYTE angle,distance=bj_carry();
    if(error>40)error=40;if(error< -40)error=-40;
    angle=(bj_angle+error/5)&63;
    px=(INT32)bj_x<<4;py=(INT32)bj_y<<4;
    bj_z=0;vz=0;age=0;bj_bounces=0;bj_roll_frames=0;tree_cooldown=0;
    airborne=(bj_club!=4);
    if(airborne) {
        vz=loft[bj_club];
        speed=((INT16)distance*256)/vz; // gravity=2 => flight duration approximately loft
        bj_z=1;
    } else speed=(UWORD)260*bj_power/100;
    speed=speed*(100-magnitude(error))/100;
    bj_vx=(INT32)bj_cos[angle]*speed/256;
    bj_vy=(INT32)bj_sin[angle]*speed/256;
}
UBYTE bj_physics_step(void) BANKED {
    INT16 dx,dy,speed;
    INT32 oldx=px,oldy=py;
    UBYTE lie,friction;
    age++;
    if(tree_cooldown)tree_cooldown--;
    if(airborne && !(age&3)) {bj_vx+=bj_wind_x;bj_vy+=bj_wind_y;}
    px+=bj_vx;py+=bj_vy;
    bj_x=(INT16)(px>>4);bj_y=(INT16)(py>>4);
    if(airborne) {bj_z+=vz;vz-=2;}
    lie=bj_terrain(bj_hole,(UBYTE)(bj_x>>4),(UBYTE)(bj_y>>4));
    if(bj_x<0 || bj_x>=2560 || bj_y<256 || bj_y>=2048) {
        // Crossing the course boundary is an immediate out-of-bounds penalty.
        bj_z=0;return BJ_SPLASH;
    }
    if(lie==BJ_TREE && bj_z<512 && !tree_cooldown) {
        px=oldx;py=oldy;bj_x=(INT16)(px>>4);bj_y=(INT16)(py>>4);
        bj_vx=-bj_vx/2;bj_vy=-bj_vy/2;tree_cooldown=12;bj_notice=2;
    }
    if(bj_z<=0) {
        bj_z=0;
        if(lie==BJ_WATER)return BJ_SPLASH;
        if(airborne) {
            bj_bounces++;
            if(vz< -16 && lie!=BJ_SAND && lie!=BJ_ROUGH && bj_bounces<3) {
                vz=-vz/4;bj_z=1;
                bj_vx=bj_vx/2;bj_vy=bj_vy/2;
            } else {
                airborne=0;vz=0;
                bj_vx=bj_vx/2;bj_vy=bj_vy/2;
            }
        }
    }
    speed=magnitude(bj_vx)+magnitude(bj_vy);
    dx=bj_x-((INT16)bj_course.cup_x<<4);dy=bj_y-((INT16)bj_course.cup_y<<4);
    // The cup accepts a slow rolling ball within 1.5 pixels. Fast putts run over it.
    if(!airborne && speed<90 && magnitude(dx)<=24 && magnitude(dy)<=24 && dx*dx+dy*dy<=576)return BJ_SUNK;
    if(!airborne) {
        bj_roll_frames++;
        friction=(lie==BJ_GREEN)?7:(lie==BJ_FAIRWAY)?14:(lie==BJ_SAND)?72:38;
        // The rendered chevrons indicate this cross slope. Static friction wins at rest.
        if(lie==BJ_GREEN && speed>20) {
            bj_vx+=bj_course.slope_x*3;
            bj_vy+=bj_course.slope_y*3;
        }
        // Drag follows the velocity vector; flat ground must not create a break.
        dx=magnitude(bj_vx);dy=magnitude(bj_vy);
        speed=(dx>dy)?dx+dy*3/8:dy+dx*3/8;
        if(speed<=friction) {bj_vx=0;bj_vy=0;}
        else {
            bj_vx=(INT32)bj_vx*(speed-friction)/speed;
            bj_vy=(INT32)bj_vy*(speed-friction)/speed;
        }
        if(!bj_vx && !bj_vy)return BJ_STOPPED;
    }
    if(age>=240) {bj_z=0;return BJ_STOPPED;}
    return BJ_MOVING;
}
