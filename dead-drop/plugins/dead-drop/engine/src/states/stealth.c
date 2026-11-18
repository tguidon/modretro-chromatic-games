#pragma bank 255
#include <gb/gb.h>
#include <gb/cgb.h>
#include <string.h>
#include "states/stealth.h"
#include "actor.h"
#include "camera.h"
#include "collision.h"
#include "data_manager.h"
#include "game_time.h"
#include "input.h"
#include "trigger.h"
#include "ui.h"
#include "vm.h"
#include "dd_font.h"
#include "dd_combat_fx.h"

/* Native scene extension: actor 1..4 guards; 5..8 sight markers;
 * actor 9 interactive console; actor 10 animated weapon effect. Standard scene resources
 * remain editable. Distances here are pixels; engine positions use 1/32px. */
static UBYTE health, ammo, crouch, sector, ready, blackout;
static UBYTE dead[28], suspicion[4], guard_hp[4], turn_wait[4], shot_wait[4];
static UWORD origin_x[4],origin_y[4],entry_x,entry_y;
static UWORD alert_timer,invuln,mission_seconds,clock_tick,kills,alerts,deaths;
static UBYTE attack_cd,notice_timer,room_timer;
static UWORD last_hud_frame;
static UBYTE hud_ready,paused,hack_progress,lockdown,phase;
static UBYTE hud[40], attributes[40];
static const char *sector_names[28]={"BOARDING PLATFORM","AFT WINCH DECK","CONTAINER SPINE","CUSTOMS LOCK","CREW PASSAGE","MESS HALL","SECURITY OFFICE","SERVICE TRUNK","BALLAST GALLERY","PUMP CONTROL","ENGINE ROOM","GENERATOR","LOWER HOLD","TANK CATWALK","SIGNAL ARCHIVE","RADIO ROOM","OFFICER QUARTERS","BRIDGE","CIPHER VAULT","MISSILE CARGO","LAUNCH CONTROL","FOREDECK","CRANE GANTRY","LIFEBOAT","INFIRMARY","ARMORY","CHART ROOM","VENTILATION"};
static WORD ab(WORD x){return x<0?-x:x;}
static UBYTE solid(WORD x,WORD y,UBYTE crawling){
 UBYTE c;if(x<0||y<0)return 1;
 c=tile_at(x>>3,y>>3);return (c&15)||((c&32)&&!crawling);
}
static UBYTE move_actor(actor_t *a, WORD dx, WORD dy, UBYTE crawl){
 WORD x=(a->pos.x+dx)>>5,y=(a->pos.y+dy)>>5;
 if(solid(x+3,y+1,crawl)||solid(x+12,y+1,crawl)||solid(x+3,y+7,crawl)||solid(x+12,y+7,crawl))return 0;
 a->pos.x+=dx;a->pos.y+=dy;return 1;
}
static UBYTE sight(WORD x,WORD y,WORD tx,WORD ty){
 WORD dx,dy,err,e2;BYTE sx,sy;
 x>>=3;y>>=3;tx>>=3;ty>>=3;
 dx=ab(tx-x);dy=-ab(ty-y);sx=x<tx?1:-1;sy=y<ty?1:-1;err=dx+dy;
 while(x!=tx||y!=ty){
  e2=err*2;if(e2>=dy){err+=dy;x+=sx;}if(e2<=dx){err+=dx;y+=sy;}
  if(tile_at(x,y)&15)return 0;
 }
 return 1;
}
static UBYTE in_front(direction_e dir,WORD dx,WORD dy,UBYTE range,UBYTE width){
 if(dir==DIR_UP)return dy<0&&-dy<range&&ab(dx)<width;
 if(dir==DIR_DOWN)return dy>=0&&dy<range&&ab(dx)<width;
 if(dir==DIR_LEFT)return dx<0&&-dx<range&&ab(dy)<width;
 return dx>=0&&dx<range&&ab(dy)<width;
}
static void sound(UBYTE effect){
 NR52_REG=0x80;NR50_REG=0x66;NR51_REG=0xFF;
 if(effect==0){NR41_REG=0;NR42_REG=0x71;NR43_REG=0x31;NR44_REG=0x80;}
 else {NR10_REG=0;NR11_REG=0x80;NR12_REG=0x82;NR13_REG=effect==1?0xC0:0x40;NR14_REG=0x86;}
}
static void print_hud(UBYTE pos,const char *s){while(*s&&pos<40){hud[pos++]=192+(*s++-32);}}
static void digit(UBYTE pos,UBYTE n){hud[pos]=192+16+n;}
static void draw_hud(void){
 UBYTE i,maxsus=0;WORD px=(PLAYER.pos.x>>5)+8,py=(PLAYER.pos.y>>5)+4;
 if(!hud_ready || (UWORD)(game_time-last_hud_frame)>2){
  VBK_REG=1;set_bkg_data(192,64,dd_font);VBK_REG=0;hud_ready=1;
 }
 last_hud_frame=game_time;
 if((game_time&7)&&win_dest_pos_y==128&&!room_timer)return;
 for(i=0;i<40;i++){hud[i]=192;attributes[i]=15;}
 print_hud(0,"HP   AM      ");
 digit(3,health);digit(8,ammo/10);digit(9,ammo%10);
 for(i=0;i<4;i++)if(suspicion[i]>maxsus)maxsus=suspicion[i];
 if(paused)print_hud(13,"PAUSED");
 else if(alert_timer)print_hud(13,"ALERT!");
 else if(maxsus>12)print_hud(13,"SEEN ");
 else if((tile_at(px>>3,py>>3)&16)||blackout)print_hud(13,"HIDDEN");
 else print_hud(13,crouch?"CROUCH":"LIT");
 if(paused){
  if(phase==0)print_hud(20,"OBJ: SECURITY CARD");
  if(phase==1)print_hud(20,"OBJ: BRIDGE MANIFEST");
  if(phase==2)print_hud(20,"OBJ: PUMP + ENGINE");
  if(phase==3)print_hud(20,"OBJ: CIPHER / CARGO");
  if(phase==4)print_hud(20,"OBJ: ERASE UPLINK");
  if(phase==5)print_hud(20,"OBJ: BOW LIFEBOAT");
 }
 else if(hack_progress){print_hud(20,"LINK ");for(i=0;i<hack_progress/12;i++)hud[25+i]=(UBYTE)221;}
 else if(notice_timer)print_hud(20,"CHECKPOINT RESTORED");
 else if(room_timer)print_hud(20,sector_names[sector]);
 else {
  print_hud(20,crouch?"LOW ":"UP  ");print_hud(25,"S");digit(26,(sector+1)/10);digit(27,(sector+1)%10);
  print_hud(30,"TIME ");digit(35,(mission_seconds/60)/10);digit(36,(mission_seconds/60)%10);print_hud(37,":");digit(38,(mission_seconds%60)/10);digit(39,mission_seconds%10);
 }
 VBK_REG=1;set_win_tiles(0,0,20,2,attributes);VBK_REG=0;set_win_tiles(0,0,20,2,hud);
 ui_set_pos(7,128);
}
static void restore_checkpoint(void){
 UBYTE i;health=5;if(ammo<6)ammo=6;alert_timer=0;invuln=180;deaths++;notice_timer=180;
 PLAYER.pos.x=entry_x;PLAYER.pos.y=entry_y;
 for(i=0;i<4;i++){actors[i+1].pos.x=origin_x[i];actors[i+1].pos.y=origin_y[i];suspicion[i]=0;shot_wait[i]=90;}
 hack_progress=0;dd_combat_reset();sound(2);
}
static void hurt(void){if(invuln)return;if(health)--health;invuln=90;sound(2);if(!health)restore_checkpoint();}
static void down_guard(UBYTE i){
 dead[sector]|=1<<i;actors[i+1].flags|=ACTOR_FLAG_HIDDEN;actors[i+5].flags|=ACTOR_FLAG_HIDDEN;
 suspicion[i]=0;kills++;sound(1);
}
void dd_command(SCRIPT_CTX *THIS) OLDCALL BANKED {
 UBYTE value=*(UWORD*)VM_REF_TO_PTR(FN_ARG0),op=*(UWORD*)VM_REF_TO_PTR(FN_ARG1);
 hud_ready=0;
 if(op==0){memset(dead,0,sizeof(dead));health=5;ammo=12;crouch=0;blackout=0;lockdown=0;phase=0;mission_seconds=clock_tick=kills=alerts=deaths=0;}
 if(op==1){sector=value;ready=0;room_timer=180;}
 if(op==2){health=5;ammo+=value;if(ammo>24)ammo=24;sound(1);}
 if(op==3)blackout=1;
 if(op==4){ui_set_pos(7,144);}
 if(op==5){UBYTE j;lockdown=1;for(j=8;j<17;j++)dead[j]=0;}
 if(op==6)phase=value;
}
void stealth_init(void) BANKED {
 camera_offset_x=0;camera_offset_y=0;camera_deadzone_x=8;camera_deadzone_y=8;
 ready=0;hud_ready=0;paused=0;attack_cd=0;hack_progress=0;
 if(!health){health=5;ammo=12;}
}
static void prepare_room(void){
 UBYTE i;entry_x=PLAYER.pos.x;entry_y=PLAYER.pos.y;alert_timer=0;invuln=90;notice_timer=0;
 for(i=0;i<4;i++){
  origin_x[i]=actors[i+1].pos.x;origin_y[i]=actors[i+1].pos.y;
  suspicion[i]=0;guard_hp[i]=1;turn_wait[i]=i*10;shot_wait[i]=90;
  if(dead[sector]&(1<<i)){actors[i+1].flags|=ACTOR_FLAG_HIDDEN;actors[i+5].flags|=ACTOR_FLAG_HIDDEN;}
 }
 dd_combat_reset();ready=1;
 if(blackout){set_bkg_palette_entry(0,0,RGB(15,19,20));set_bkg_palette_entry(0,1,RGB(7,11,14));set_bkg_palette_entry(1,0,RGB(12,16,17));set_bkg_palette_entry(1,1,RGB(6,10,13));}
 if(lockdown)set_bkg_palette_entry(2,0,RGB(31,12,7));
}
static void attack(UBYTE pistol){
 UBYTE i,best=255;WORD nearest=200,dist,dx,dy;
 if(attack_cd)return;
 if(pistol&&!ammo){sound(2);return;}
 attack_cd=pistol?22:18;
 if(pistol){ammo--;sound(0);}
 for(i=0;i<4;i++){
  if(dead[sector]&(1<<i))continue;
  dx=((WORD)actors[i+1].pos.x-(WORD)PLAYER.pos.x)>>5;dy=((WORD)actors[i+1].pos.y-(WORD)PLAYER.pos.y)>>5;
  dist=ab(dx)+ab(dy);
  if(in_front(PLAYER.dir,dx,dy,pistol?112:23,pistol?11:18)&&dist<nearest&&sight((PLAYER.pos.x>>5)+8,(PLAYER.pos.y>>5)+4,(actors[i+1].pos.x>>5)+8,(actors[i+1].pos.y>>5)+4)){best=i;nearest=dist;}
 }
 if(best!=255){
  if(!pistol && suspicion[best]>40) hurt();
  down_guard(best);
 } else if(!pistol) {
  actor_t *obj=&actors[9];
  dx=((WORD)obj->pos.x-(WORD)PLAYER.pos.x)>>5;dy=((WORD)obj->pos.y-(WORD)PLAYER.pos.y)>>5;
  if(ab(dx)<25&&ab(dy)<25&&obj->script.bank){hack_progress=1;}
 }
 /* Show attacks on both hits and misses; terminal use is not a knife swing. */
 if(pistol || !hack_progress){
  UBYTE travel=112;
  if(best!=255){
   dx=((WORD)actors[best+1].pos.x-(WORD)PLAYER.pos.x)>>5;
   dy=((WORD)actors[best+1].pos.y-(WORD)PLAYER.pos.y)>>5;
   travel=(PLAYER.dir==DIR_LEFT||PLAYER.dir==DIR_RIGHT)?ab(dx):ab(dy);
  }
  dd_combat_start(pistol,PLAYER.dir,travel,best!=255);
 }
 /* Suppressed fire is audible only nearby; distant patrols stay unaware. */
 if(pistol)for(i=0;i<4;i++)if(!(dead[sector]&(1<<i))){
  dx=((WORD)actors[i+1].pos.x-(WORD)PLAYER.pos.x)>>5;dy=((WORD)actors[i+1].pos.y-(WORD)PLAYER.pos.y)>>5;
  if(ab(dx)+ab(dy)<52)suspicion[i]=48;
 }
}
void stealth_update(void) BANKED {
 UBYTE i,seen,shade,speed;WORD dx,dy,gx,gy,px,py;actor_t *a,*marker;direction_e dir;
 if(!ready)prepare_room();
 if(INPUT_START_PRESSED){paused=!paused;sound(1);}
 if(paused){draw_hud();return;}
 if(INPUT_SELECT_PRESSED)crouch=!crouch;
 if(invuln)invuln--;if(attack_cd)attack_cd--;if(notice_timer)notice_timer--;if(room_timer)room_timer--;
 if(++clock_tick==60){clock_tick=0;mission_seconds++;}
 if((game_time&31)==0){
  static const UBYTE pulse[8]={0x42,0x42,0x71,0x42,0x9D,0x71,0x23,0x71};
  NR52_REG=0x80;NR50_REG=0x66;NR51_REG=0xFF;
  NR21_REG=0x80;NR22_REG=alert_timer?0x51:0x21;NR23_REG=pulse[(game_time>>5)&7];NR24_REG=alert_timer?0x87:0x85;
 }
 if(alert_timer)alert_timer--;
 PLAYER.flags&=~ACTOR_FLAG_HIDDEN;if(invuln&&((game_time&7)<3))PLAYER.flags|=ACTOR_FLAG_HIDDEN;
 dir=DIR_NONE;dx=dy=0;speed=crouch?16:32;
 if(INPUT_LEFT){dx=-speed;dir=DIR_LEFT;}else if(INPUT_RIGHT){dx=speed;dir=DIR_RIGHT;}
 else if(INPUT_UP){dy=-speed;dir=DIR_UP;}else if(INPUT_DOWN){dy=speed;dir=DIR_DOWN;}
 if(dir!=DIR_NONE){move_actor(&PLAYER,dx,dy,crouch);actor_set_dir(&PLAYER,dir,1);}else actor_set_anim_idle(&PLAYER);
 if(trigger_activate_at_intersection(&PLAYER.bounds,&PLAYER.pos,FALSE)){hud_ready=0;return;}
 if(INPUT_A_PRESSED)attack(0);if(INPUT_B_PRESSED)attack(1);
 dd_combat_update();
 if(hack_progress){
  dx=((WORD)actors[9].pos.x-(WORD)PLAYER.pos.x)>>5;dy=((WORD)actors[9].pos.y-(WORD)PLAYER.pos.y)>>5;
  if(!INPUT_A||ab(dx)>24||ab(dy)>24)hack_progress=0;
  else if(++hack_progress>=180){hack_progress=0;ui_set_pos(7,144);hud_ready=0;script_execute(actors[9].script.bank,actors[9].script.ptr,0,1,0);return;}
 }
 px=(PLAYER.pos.x>>5)+8;py=(PLAYER.pos.y>>5)+4;
 shade=((tile_at(px>>3,py>>3)&16)||blackout);
 for(i=0;i<4;i++){
  if(dead[sector]&(1<<i))continue;
  a=&actors[i+1];marker=&actors[i+5];gx=(a->pos.x>>5)+8;gy=(a->pos.y>>5)+4;dx=px-gx;dy=py-gy;
  /* Only one expensive line-of-sight test per four frames per guard. */
  if((game_time&3)==i){
   seen=in_front(a->dir,dx,dy,shade?(crouch?30:48):88,12+((ab(dx)+ab(dy))>>2))&&sight(gx,gy,px,py);
   if(ab(dx)<12&&ab(dy)<12)seen=1;
   if(seen){
    speed=shade?(crouch?2:4):(crouch?5:9);
    if(suspicion[i]<90)suspicion[i]+=speed;
    if(suspicion[i]>=90){if(!alert_timer){alerts++;sound(2);}alert_timer=480;}
   }else if(suspicion[i])suspicion[i]--;
  }
  if(alert_timer&&suspicion[i]>40){
   dir=ab(dx)>ab(dy)?(dx<0?DIR_LEFT:DIR_RIGHT):(dy<0?DIR_UP:DIR_DOWN);
   if(ab(dx)+ab(dy)>26){
    if(ab(dx)>ab(dy)){if(!move_actor(a,dx<0?-24:24,0,0)&&dy)move_actor(a,0,dy<0?-24:24,0);}
    else if(!move_actor(a,0,dy<0?-24:24,0)&&dx)move_actor(a,dx<0?-24:24,0,0);
   }
   actor_set_dir(a,dir,1);
   if(shot_wait[i])shot_wait[i]--;
   else {shot_wait[i]=100;if(ab(dx)+ab(dy)<112&&sight(gx,gy,px,py))hurt();}
  }else{
   if(turn_wait[i]){turn_wait[i]--;actor_set_anim_idle(a);}
   else{
    dx=dy=0;speed=lockdown?16:12;if(a->dir==DIR_LEFT)dx=-speed;if(a->dir==DIR_RIGHT)dx=speed;if(a->dir==DIR_UP)dy=-speed;if(a->dir==DIR_DOWN)dy=speed;
    if(!move_actor(a,dx,dy,0)||ab((WORD)a->pos.x-(WORD)origin_x[i])>1536||ab((WORD)a->pos.y-(WORD)origin_y[i])>1536){
     dir=a->dir==DIR_LEFT?DIR_RIGHT:a->dir==DIR_RIGHT?DIR_LEFT:a->dir==DIR_UP?DIR_DOWN:DIR_UP;
     actor_set_dir(a,dir,0);turn_wait[i]=50;
    }else actor_set_anim_moving(a);
   }
  }
  marker->pos=a->pos;actor_set_dir(marker,a->dir,0);
  if(a->dir==DIR_UP)marker->pos.y-=768;if(a->dir==DIR_DOWN)marker->pos.y+=768;
  if(a->dir==DIR_LEFT)marker->pos.x-=768;if(a->dir==DIR_RIGHT)marker->pos.x+=768;
  if(suspicion[i]>35 && (game_time&8))marker->flags|=ACTOR_FLAG_HIDDEN;else marker->flags&=~ACTOR_FLAG_HIDDEN;
 }
 draw_hud();
}
