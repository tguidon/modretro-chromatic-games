#pragma bank 255
#include "states/golf.h"
#include "ui.h"
#include "interrupts.h"

UBYTE bj_view_active,bj_view_zoom,bj_view_busy;
INT16 bj_view_x,bj_view_y;
static UBYTE tiles[20],attrs[20],top[40],bottom[40];
void bj_view_tiles(void) BANKED;
static UBYTE surface(INT16 x,UBYTE *row) {
    UBYTE cell,value;
    if(x<0 || x>=160)return BJ_ROUGH;
    cell=x>>1;value=row[cell>>1];return cell&1?value>>4:value&15;
}
static void render(void) {
    UBYTE x,y,i,pal,mask,c[4];
    INT16 wx,wy;
    for(y=0;y<12;y++) {
        wy=bj_view_y+(UWORD)y*8/bj_view_zoom;
        bj_terrain_row(bj_hole,wy,top);bj_terrain_row(bj_hole,wy+4/bj_view_zoom,bottom);
        for(x=0;x<20;x++) {
            wx=bj_view_x+(UWORD)x*8/bj_view_zoom;
            c[0]=surface(wx,top);c[1]=surface(wx+4/bj_view_zoom,top);
            c[2]=surface(wx,bottom);c[3]=surface(wx+4/bj_view_zoom,bottom);
            pal=0;for(i=0;i<4;i++)if(c[i]>pal)pal=c[i];
            mask=0;for(i=0;i<4;i++)if(c[i]==pal)mask|=1<<i;
            tiles[x]=pal*16+mask;attrs[x]=8+(pal==BJ_TREE?0:pal);
            if(bj_view_zoom==2 && pal==BJ_GREEN && mask==15 && !(x&1) && !(y&1)) {
                tiles[x]=96+((x+y)&3);
                if(bj_course.slope_x<0)attrs[x]|=32;
                if(bj_course.slope_y<0)attrs[x]|=64;
            }
        }
        VBK_REG=0;set_win_tiles(0,y+2,20,1,tiles);
        VBK_REG=1;set_win_tiles(0,y+2,20,1,attrs);
    }
    VBK_REG=0;
}
void bj_view_open(UBYTE zoom,INT16 x,INT16 y) BANKED {
    bj_view_busy=1;bj_view_zoom=zoom;bj_view_x=x-80/zoom;bj_view_y=y-64/zoom;
    bj_view_tiles();bj_view_grid();render();bj_view_active=1;show_actors_on_overlay=1;ui_set_pos(0,0);
}
void bj_view_follow(void) BANKED {
    INT16 x=bj_x>>4,y=bj_y>>4;
    if(x-bj_view_x<60 || x-bj_view_x>100 || y-bj_view_y<44 || y-bj_view_y>76) {
        bj_view_x=x-80;bj_view_y=y-64;render();
    }
}
void bj_view_close(void) BANKED {bj_view_active=0;show_actors_on_overlay=0;ui_set_pos(0,144);}
