#pragma bank 255
#include "states/golf.h"
#include "states/birdie_direction.h"

// Position and horizontal speed use 8 fractional bits; altitude uses 4.
// Gravity, drag and slope acceleration are integrated every game update.
INT16 bj_z, bj_vx, bj_vy, bj_target_x, bj_target_y;
UBYTE bj_spread,bj_fine,bj_putt_long,bj_lip;
INT8 bj_wind_x, bj_wind_y;
UBYTE bj_bounces, bj_roll_frames;
static INT32 px,py;
static INT16 vz;
static UWORD age;
static UBYTE tree_cooldown, airborne,cup_cooldown;
static const UBYTE ranges[5]={54,45,33,22,22};
static const UBYTE loft[4]={44,50,56,64};

static INT16 magnitude(INT16 n) {return n<0?-n:n;}
UBYTE bj_carry(void) BANKED {
    UWORD distance=(UWORD)ranges[bj_club]*bj_power/100;
    UBYTE lie=bj_terrain(bj_hole,(UBYTE)(bj_x>>4),(UBYTE)(bj_y>>4));
    if(bj_club==4)distance=(UWORD)(bj_putt_long?28:12)*bj_power/100;
    else if(bj_club!=3) {
        if(lie==BJ_SAND)distance=distance/2;
        else if(lie==BJ_ROUGH)distance=distance*3/4;
    }
    return distance?distance:1;
}
static INT16 direction(UBYTE heading,UBYTE y) {
    UBYTE a=heading>>2,f=heading&3;
    const INT16 *table=y?bj_sin:bj_cos;
    return table[a]+((INT16)(table[(a+1)&63]-table[a])*f/4);
}
static UWORD root(UWORD value) {
    UWORD result=0,bit=16384;
    while(bit>value)bit>>=2;
    while(bit) {if(value>=result+bit) {value-=result+bit;result=(result>>1)+bit;}else result>>=1;bit>>=2;}
    return result;
}
void bj_predict(void) BANKED {
    UBYTE distance=bj_carry(),lie=bj_terrain(bj_hole,bj_x>>4,bj_y>>4);
    UWORD time=bj_club==4?0:loft[bj_club];
    bj_target_x=(bj_x>>4)+((INT32)direction((bj_angle<<2)+(bj_club==4?bj_fine:0),0)*distance/256);
    bj_target_y=(bj_y>>4)+((INT32)direction((bj_angle<<2)+(bj_club==4?bj_fine:0),1)*distance/256);
    // Same quarter-rate wind acceleration as flight; this is carry, not rollout.
    bj_target_x+=(INT32)bj_wind_x*time*time/2048;
    bj_target_y+=(INT32)bj_wind_y*time*time/2048;
    bj_spread=bj_club==4?1:2+distance/18+(lie==BJ_ROUGH?2:lie==BJ_SAND?3:0);
}
void bj_physics_start(void) BANKED {
    INT16 speed,error=bj_accuracy;
    UBYTE angle,distance=bj_carry();
    if(error>40)error=40;if(error< -40)error=-40;
    angle=(bj_angle+error/5)&63;
    px=(INT32)bj_x<<4;py=(INT32)bj_y<<4;
    bj_z=0;vz=0;age=0;bj_bounces=0;bj_roll_frames=0;tree_cooldown=0;cup_cooldown=0;bj_lip=0;
    airborne=(bj_club!=4);
    if(airborne) {
        vz=loft[bj_club];
        speed=((INT16)distance*256)/vz; // gravity=2 => flight duration approximately loft
        bj_z=1;
    } else {
        // Linear distance meter. Integer square root converts it to kinetic speed.
        // Factor four keeps the square-root argument within 16 bits.
        speed=root((UWORD)(bj_putt_long?28:12)*bj_power*12)*2;
    }
    speed=(INT32)speed*(100-magnitude(error))/100;
    if(bj_club==4) {
        angle=(bj_angle<<2)+bj_fine+error/4;
        bj_vx=(INT32)direction(angle,0)*speed/256;
        bj_vy=(INT32)direction(angle,1)*speed/256;
    } else {
        bj_vx=(INT32)bj_cos[angle]*speed/256;
        bj_vy=(INT32)bj_sin[angle]*speed/256;
    }
}
UBYTE bj_physics_step(void) BANKED {
    INT16 dx,dy,speed;
    INT32 oldx=px,oldy=py;
    UBYTE lie,friction;
    age++;
    if(cup_cooldown)cup_cooldown--;
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
    if(!airborne && !cup_cooldown && magnitude(dx)<=28 && magnitude(dy)<=28 && dx*dx+dy*dy<=784) {
        if(speed<125)return BJ_SUNK;
        // A fast edge strike loses energy and glances around the rim.
        if(speed<260 && dx*dx+dy*dy>144) {
            INT16 old=bj_vx;
            bj_vx=(bj_vx*3-bj_vy)/4;bj_vy=(bj_vy*3+old)/4;
            cup_cooldown=12;bj_lip=1;bj_notice=6;
        }
    }
    if(!airborne) {
        bj_roll_frames++;
        friction=(lie==BJ_GREEN)?10:(lie==BJ_FAIRWAY)?14:(lie==BJ_SAND)?72:38;
        // The rendered chevrons indicate this cross slope. Static friction wins at rest.
        if(lie==BJ_GREEN && speed>32) {
            bj_vx+=bj_course.slope_x*5;
            bj_vy+=bj_course.slope_y*5;
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
