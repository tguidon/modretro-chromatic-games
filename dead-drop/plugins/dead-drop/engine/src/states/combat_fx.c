#pragma bank 255
#include "dd_combat_fx.h"
#include "actor.h"
#include "collision.h"
#include "data_manager.h"
#include "data/states_defines.h"

/* Actor ten is the existing shared effect slot: no extra actors or OAM slots.
 * Presentation is separate from the existing immediate combat resolution. */
static UBYTE active, age, firearm, end_distance, connected;
static UBYTE player_pose, effect_pose;
static direction_e attack_direction;
static upoint16_t shot_origin;

static void pose(actor_t *actor, UBYTE state, UBYTE *previous) {
 if(*previous!=state){
  load_animations(actor->sprite.ptr,actor->sprite.bank,state,actor->animations);
  *previous=state;
 }
 actor_set_dir(actor,attack_direction,FALSE);
 actor_reset_anim(actor);
}
static void place_effect(UBYTE distance) {
 actor_t *fx=&actors[10];
 WORD x,y;
 fx->pos=firearm?shot_origin:PLAYER.pos;
 x=fx->pos.x>>5;y=fx->pos.y>>5;
 if(attack_direction==DIR_LEFT)x-=distance;
 if(attack_direction==DIR_RIGHT)x+=distance;
 if(attack_direction==DIR_UP)y-=distance;
 if(attack_direction==DIR_DOWN)y+=distance;
 if(x<0)x=0;if(y<0)y=0;
 fx->pos.x=(UWORD)x<<5;fx->pos.y=(UWORD)y<<5;
}
void dd_combat_reset(void) BANKED {
 active=0;age=0;player_pose=0;effect_pose=255;
 if(PLAYER.sprite.bank){
  load_animations(PLAYER.sprite.ptr,PLAYER.sprite.bank,0,PLAYER.animations);
  actor_set_anim_idle(&PLAYER);
 }
 actors[10].flags|=ACTOR_FLAG_HIDDEN;
}
void dd_combat_start(UBYTE pistol,direction_e direction,UBYTE distance,UBYTE hit) BANKED {
 UBYTE d;WORD x,y;
 active=1;age=0;firearm=pistol;attack_direction=direction;connected=hit;
 shot_origin=PLAYER.pos;effect_pose=255;
 end_distance=distance>112?112:distance;
 if(end_distance<8)end_distance=8;
 /* Stop a missed tracer at the first cover tile, as the damage ray does. */
 if(pistol)for(d=2;d<=end_distance;d+=2){
  x=(shot_origin.x>>5)+8;y=(shot_origin.y>>5)+4;
  if(direction==DIR_LEFT)x-=d;if(direction==DIR_RIGHT)x+=d;
  if(direction==DIR_UP)y-=d;if(direction==DIR_DOWN)y+=d;
  if(x<0||y<0||(tile_at(x>>3,y>>3)&15)){end_distance=d;connected=1;break;}
 }
 actors[10].flags&=~ACTOR_FLAG_HIDDEN;
}
void dd_combat_update(void) BANKED {
 UBYTE state,distance;
 if(!active)return;
 if(age>=(firearm?20:18)){dd_combat_reset();return;}
 if(firearm){
  pose(&PLAYER,age<8?DD_POSE_SHOOT:0,&player_pose);
  if(age<5){state=DD_POSE_SHOOT;distance=end_distance<10?end_distance:10;}
  else {
   distance=10+(age-5)*10;
   if(distance>=end_distance){
    distance=end_distance;state=DD_FX_IMPACT;
    if(!connected){actors[10].flags|=ACTOR_FLAG_HIDDEN;age++;return;}
   }else state=DD_FX_TRAIL;
  }
 } else {
  state=age<4?DD_POSE_WINDUP:age<11?DD_POSE_SWEEP:DD_POSE_FOLLOW;
  pose(&PLAYER,state,&player_pose);
  distance=age<4?6:age<11?12:10;
 }
 place_effect(distance);
 pose(&actors[10],state,&effect_pose);
 actors[10].flags&=~ACTOR_FLAG_HIDDEN;
 age++;
}
