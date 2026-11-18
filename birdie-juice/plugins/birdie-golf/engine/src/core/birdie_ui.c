#pragma bank 255
#include <string.h>
#include "states/golf.h"
#include "ui.h"

static UBYTE bj_text_tiles[20];
static char bj_line[21];
static const char * const bj_clubs[5]={"DRIVER","5 WOOD","7 IRON","WEDGE ","PUTTER"};
static const char * const bj_lies[6]={"ROUGH","FAIR ","GREEN","SAND ","WATER","TREES"};
static const char * const bj_card_names[9]={"MORN DEW","SQUEEZE","DOGLEG","SANDWEDG","CREEKSID","ISLAND","LONGPOUR","ORCHARD","LASTCALL"};
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
void bj_close_panel(void) BANKED {ui_set_pos(0,144);}
void bj_draw_hud(void) BANKED {
    UBYTE lie=bj_terrain(bj_hole,(UBYTE)(bj_x>>4),(UBYTE)(bj_y>>4));
    bj_blank();bj_num(0,bj_hole+1,2);bj_put(3,bj_course.name);bj_text(0,bj_line,0);
    bj_blank();bj_put(0,"PAR ");bj_num(4,bj_course.par,1);bj_put(6,"SHOT ");bj_num(11,bj_strokes,2);bj_put(14,"T:");bj_num(17,bj_total,3);bj_text(1,bj_line,0);
    bj_blank();bj_put(0,bj_clubs[bj_club]);bj_put(8,"PWR");bj_num(12,bj_power,3);bj_put(15,"%");bj_put(18,"B>");bj_text(16,bj_line,0);
    bj_blank();
    if(bj_notice==1)bj_put(0,"WATER +1 / DROP BALL");
    else if(bj_notice==2)bj_put(0,"TREES / TRY A WEDGE");
    else {bj_put(0,bj_lies[lie]);bj_put(6,"A HIT ST CARD");}
    bj_text(17,bj_line,0);
}
void bj_draw_panel(void) BANKED {
    UBYTE row,i;
    bj_hole_t hole;
    for(row=0;row<18;row++)bj_text(row,"",1);
    if(bj_mode==BJ_TITLE) {
        bj_text(2,"     B I R D I E",1);
        bj_text(4,"      J U I C E",1);
        bj_text(6,"    SUNRISE NINE",1);
        bj_text(8,"  9 HOLES / PAR 36",1);
        bj_text(10,"  A LITTLE GOLF.",1);
        bj_text(11,"  A LOT OF SUNSHINE.",1);
        bj_text(14,"    A  TEE OFF",1);
        bj_text(16,"  START  HOW TO PLAY",1);
    } else if(bj_mode==BJ_HELP) {
        bj_text(1,"    HOW TO PLAY",1);
        bj_text(3,"LEFT/RIGHT  AIM",1);
        bj_text(4,"UP/DOWN     POWER",1);
        bj_text(5,"A           SWING",1);
        bj_text(6,"B / SELECT  CLUB",1);
        bj_text(7,"START       CARD",1);
        bj_text(9,"CROSSHAIR = LANDING",1);
        bj_text(10,"AUTO AIM FACES PIN",1);
        bj_text(11,"SAND? USE THE WEDGE",1);
        bj_text(12,"WATER COSTS 1 SHOT",1);
        bj_text(13,"PUTT ON THE GREEN",1);
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
