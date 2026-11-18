#pragma bank 255
#include <string.h>
#include "states/golf.h"
#include "ui.h"

static UBYTE bj_text_tiles[20];
static char bj_line[21];
static UBYTE bj_target_power;
static UBYTE bj_meter_last_mode, bj_meter_text_tick;
static const char * const bj_clubs[5]={"DRIVER","5 WOOD","7 IRON","WEDGE ","PUTTER"};
static const char * const bj_lies[6]={"ROUGH","FAIR ","GREEN","SAND ","WATER","TREES"};
static const char * const bj_card_names[9]={"MORN DEW","SQUEEZE","DOGLEG","SANDWEDG","CREEKSID","ISLAND","LONGPOUR","ORCHARD","LASTCALL"};
static UBYTE bj_wind_speed(void) {
    UBYTE x=bj_wind_x<0?-bj_wind_x:bj_wind_x,y=bj_wind_y<0?-bj_wind_y:bj_wind_y;
    return (x>y?x:y)*2;
}
static void bj_text(UBYTE row,const char *text,UBYTE window) {
    UBYTE i=0;
    while(i<20) {UBYTE c=*text;if(c)text++;else c=' ';if(c<32||c>95)c='?';bj_text_tiles[i++]=128+c-32;}
    VBK_REG=0;
    if(window)set_win_tiles(0,row,20,1,bj_text_tiles);else set_bkg_tiles(0,row,20,1,bj_text_tiles);
    memset(bj_text_tiles,7,20);VBK_REG=1;
    if(window)set_win_tiles(0,row,20,1,bj_text_tiles);else set_bkg_tiles(0,row,20,1,bj_text_tiles);
    VBK_REG=0;
}
static void bj_blank(void) {memset(bj_line,' ',20);bj_line[20]=0;}
static void bj_put(UBYTE x,const char *s) {while(*s && x<20)bj_line[x++]=*s++;}
static void bj_num(UBYTE x,UWORD n,UBYTE digits) {while(digits){bj_line[x+digits-1]='0'+n%10;n/=10;digits--;}}
static void bj_relative(UBYTE x,INT16 n) {bj_line[x]=(n>0)?'+':(n<0)?'-':'E';if(n<0)n=-n;bj_num(x+1,(UWORD)n,2);}
void bj_close_panel(void) BANKED {bj_view_close();}
void bj_draw_hud(void) BANKED {
    INT16 dx=(bj_x>>4)-bj_course.cup_x,dy=(bj_y>>4)-bj_course.cup_y;
    UWORD yards;
    UBYTE lie=bj_terrain(bj_hole,(UBYTE)(bj_x>>4),(UBYTE)(bj_y>>4));
    bj_predict();
    if(dx<0)dx=-dx;if(dy<0)dy=-dy;
    yards=((dx>dy)?dx+dy*3/8:dy+dx*3/8)*3;
    bj_blank();bj_num(0,bj_hole+1,2);bj_put(3,bj_course.name);bj_text(0,bj_line,bj_view_active);
    bj_blank();bj_put(0,"PAR ");bj_num(4,bj_course.par,1);bj_put(6,"SHOT ");bj_num(11,bj_strokes,2);bj_num(15,yards,3);bj_put(18,"Y");bj_text(1,bj_line,bj_view_active);
    bj_blank();bj_put(0,bj_clubs[bj_club]);bj_num(7,(UWORD)bj_carry()*3,3);bj_put(10,"Y P");bj_num(13,bj_power,3);bj_put(16,"%");bj_put(18,"B>");bj_text(16,bj_line,bj_view_active);
    bj_blank();
    if(bj_notice==1)bj_put(0,"WATER +1 / DROP BALL");
    else if(bj_notice==2)bj_put(0,"TREES / TRY A WEDGE");
    else if(bj_notice==4)bj_put(0,"NICE SHOT!");
    else if(bj_notice==5)bj_put(0,bj_accuracy<0?"LATE / PULLED LEFT":"EARLY / PUSHED RIGHT");
    else {bj_put(0,bj_lies[bj_terrain(bj_hole,(UBYTE)bj_target_x,(UBYTE)bj_target_y)]);bj_put(5," +/-");bj_num(9,bj_spread*3,2);bj_put(11,"Y");bj_put(14,"W:");bj_put(16,bj_wind_x<0?"<":bj_wind_x>0?">":"-");bj_put(17,bj_wind_y<0?"^":"V");bj_num(18,bj_wind_speed(),1);}
    bj_text(17,bj_line,bj_view_active);
    if(bj_view_active) {bj_text(14,bj_z?"     BALL IN FLIGHT":"     BOUNCE / ROLL",1);bj_text(15,"",1);}
}
void bj_shot_meter(void) BANKED {
    UBYTE i,pos,pixel,target,mask,tiles[16],attrs[16],cursor[16];
    static const UBYTE bar[16]={255,255,255,255,135,135,135,135,135,135,135,135,135,135,255,255};
    static const UBYTE mark[16]={231,231,195,195,129,129,0,0,129,129,195,195,231,231,255,255};
    INT16 meter=bj_meter;
    if(meter<0)meter=0;if(meter>100)meter=100;
    pixel=(UWORD)meter*127/100;pos=pixel>>3;
    target=(UWORD)(bj_mode==BJ_POWER?bj_target_power:10)*127/800;
    if(target>15)target=15;
    for(i=0;i<16;i++) {tiles[i]=109;attrs[i]=11;}
    if(bj_mode!=BJ_POWER) {attrs[0]=10;attrs[1]=10;attrs[2]=10;}
    tiles[target]=111;attrs[target]=10;tiles[pos]=110;attrs[pos]=15;
    mask=128>>(pixel&7);
    for(i=0;i<16;i++)cursor[i]=~mask;
    VBK_REG=1;set_bkg_data(109,1,bar);set_bkg_data(110,1,cursor);set_bkg_data(111,1,mark);
    set_win_tiles(2,15,16,1,attrs);VBK_REG=0;set_win_tiles(2,15,16,1,tiles);
    if(bj_meter_last_mode!=bj_mode) {
        bj_meter_last_mode=bj_mode;bj_meter_text_tick=0;
        bj_text(17,bj_mode==BJ_POWER?"A SET POWER B CANCEL":bj_mode==BJ_ACCURACY?"A HIT GREEN DIAMOND":"     FOLLOW THROUGH",1);
    }
    if(bj_meter_text_tick++&3)return;
    bj_blank();bj_put(0,"PWR ");bj_num(4,bj_mode==BJ_POWER?meter:bj_power,3);
    if(bj_mode==BJ_POWER) {bj_put(9,"TARGET ");bj_num(16,bj_target_power,3);}
    else if(bj_mode==BJ_SWING) {bj_put(9,bj_accuracy>=-3 && bj_accuracy<=3?"PURE!":bj_accuracy<0?"LATE / HOOK":"EARLY/SLICE");}
    else {bj_put(9,"HIT DIAMOND");}
    bj_text(16,bj_line,1);
}
void bj_shot_open(void) BANKED {
    UBYTE row,lie=bj_terrain(bj_hole,(UBYTE)(bj_x>>4),(UBYTE)(bj_y>>4));
    bj_target_power=bj_power;
    bj_meter_last_mode=255;bj_meter_text_tick=0;
    for(row=0;row<18;row++)bj_text(row,"",1);
    bj_blank();bj_put(0,"HOLE ");bj_num(5,bj_hole+1,1);bj_put(8,"PAR ");bj_num(12,bj_course.par,1);bj_put(14,"S:");bj_num(16,bj_strokes+1,2);bj_text(0,bj_line,1);
    bj_blank();bj_put(0,bj_clubs[bj_club]);bj_put(8,"WIND ");bj_put(13,bj_wind_x<0?"<":bj_wind_x>0?">":"-");bj_put(14,bj_wind_y<0?"^":"V");bj_num(16,bj_wind_speed(),1);bj_put(17,"MPH");bj_text(1,bj_line,1);
    bj_shot_art();
    bj_blank();bj_put(0,bj_lies[lie]);bj_put(7,bj_club==4?"READ BREAK":"TIME YOUR HIT");bj_text(14,bj_line,1);
    bj_shot_meter();text_drawn=1;ui_set_pos(0,0);
}
void bj_draw_panel(void) BANKED {
    UBYTE row,i;
    bj_hole_t hole;
    for(row=0;row<18;row++)bj_text(row,"",1);
    if(bj_mode==BJ_TITLE) {
        bj_shot_art();
        bj_text(0,"    BIRDIE JUICE",1);
        bj_text(1,"  THE SUNRISE NINE",1);
        bj_text(14,"  9 HOLES / PAR 36",1);
        bj_text(16,"    A  TEE OFF",1);
        bj_text(17,"  START  HOW TO PLAY",1);
    } else if(bj_mode==BJ_HELP) {
        bj_text(1,"    HOW TO PLAY",1);
        bj_text(3,"LEFT/RIGHT  AIM",1);
        bj_text(4,"UP/DOWN  TARGET PWR",1);
        bj_text(5,"A START / POWER / HIT",1);
        bj_text(6,"B / SELECT  CLUB",1);
        bj_text(7,"START       CARD",1);
        bj_text(9,"HIT GREEN ON RETURN",1);
        bj_text(10,"WIND BENDS AIR SHOTS",1);
        bj_text(11,"SAND? USE THE WEDGE",1);
        bj_text(12,"RING = CARRY SPREAD",1);
        bj_text(13,"LANDING LIE IN HUD",1);
        bj_text(14,"12 SHOTS = PICK UP",1);
        bj_text(16,"    A / B  BACK",1);
    } else if(bj_mode==BJ_CARD) {
        bj_text(0,"BIRDIE JUICE  PAR 36",1);
        bj_text(2,"HOLE        PAR SHOT",1);
        for(i=0;i<9;i++) {
            bj_read_hole(i,&hole);bj_blank();bj_num(1,i+1,2);bj_put(4,bj_card_names[i]);bj_num(13,hole.par,1);
            if(bj_scores[i])bj_num(17,bj_scores[i],2);else bj_put(17,"--");
            bj_text(i+3,bj_line,1);
        }
        bj_blank();bj_put(1,"TOTAL ");bj_num(7,bj_total,3);bj_put(11,"TO PAR");
        if(bj_hole==8 && bj_scores[8])bj_relative(17,(INT16)bj_total-36);
        else {UBYTE pars=0;for(i=0;i<9;i++)if(bj_scores[i]){bj_read_hole(i,&hole);pars+=hole.par;}bj_relative(17,(INT16)bj_total-(INT16)pars-(bj_scores[bj_hole]?0:bj_strokes));}
        bj_text(13,bj_line,1);
        if(bj_hole==8 && bj_scores[8]) {bj_text(15,"  ROUND COMPLETE!",1);bj_text(17," A PLAY AGAIN B BACK",1);}
        else bj_text(16,"   A / B  BACK",1);
    } else {
        bj_text(2,"     HOLE IN!",1);bj_blank();bj_num(1,bj_hole+1,2);bj_put(4,bj_course.name);bj_text(4,bj_line,1);
        bj_blank();bj_put(3,"PAR ");bj_num(7,bj_course.par,1);bj_put(10,"SHOTS ");bj_num(16,bj_strokes,2);bj_text(6,bj_line,1);
        if(bj_notice==3)bj_text(8,"    PICKED UP",1);
        else if(bj_strokes==1)bj_text(8,"    HOLE IN ONE!",1);
        else if(bj_strokes+2<=bj_course.par)bj_text(8,"       EAGLE!",1);
        else if(bj_strokes+1==bj_course.par)bj_text(8,"      BIRDIE!",1);
        else if(bj_strokes==bj_course.par)bj_text(8,"       PAR!",1);
        else bj_text(8,"  ON TO THE NEXT!",1);
        bj_blank();bj_put(3,"ROUND TOTAL ");bj_num(15,bj_total,3);bj_text(11,bj_line,1);
        bj_text(14,"    A  NEXT HOLE",1);bj_text(16,"  START  SCORECARD",1);
    }
    text_drawn=1;ui_set_pos(0,0);
}
