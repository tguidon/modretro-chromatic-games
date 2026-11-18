#pragma bank 255
#include "states/golf.h"
#include "ui.h"

UBYTE bj_view_active,bj_view_zoom;
INT16 bj_view_x,bj_view_y;
static UBYTE tiles[20],attrs[20];
void bj_view_tiles(void) BANKED;
static UBYTE surface(INT16 x,INT16 y) {
    if(x<0 || x>=160 || y<16 || y>=128)return BJ_ROUGH;
    return bj_terrain(bj_hole,x,y);
}
static void render(void) {
    UBYTE x,y,i,pal,mask,c[4];
    INT16 wx,wy;
    for(y=0;y<12;y++) {
        for(x=0;x<20;x++) {
            wx=bj_view_x+(UWORD)x*8/bj_view_zoom;
            wy=bj_view_y+(UWORD)y*8/bj_view_zoom;
            c[0]=surface(wx,wy);c[1]=surface(wx+4/bj_view_zoom,wy);
            c[2]=surface(wx,wy+4/bj_view_zoom);c[3]=surface(wx+4/bj_view_zoom,wy+4/bj_view_zoom);
            pal=0;for(i=0;i<4;i++)if(c[i]>pal)pal=c[i];
            mask=0;for(i=0;i<4;i++)if(c[i]==pal)mask|=1<<i;
            tiles[x]=pal*16+mask;attrs[x]=8+(pal==BJ_TREE?0:pal);
        }
        VBK_REG=0;set_win_tiles(0,y+2,20,1,tiles);
        VBK_REG=1;set_win_tiles(0,y+2,20,1,attrs);
    }
    VBK_REG=0;
}
void bj_view_open(UBYTE zoom,INT16 x,INT16 y) BANKED {
    bj_view_zoom=zoom;bj_view_x=x-80/zoom;bj_view_y=y-64/zoom;
    bj_view_tiles();render();bj_view_active=1;ui_set_pos(0,0);
}
void bj_view_follow(void) BANKED {
    INT16 x=bj_x>>4,y=bj_y>>4;
    if(x-bj_view_x<60 || x-bj_view_x>100 || y-bj_view_y<44 || y-bj_view_y>76) {
        bj_view_x=x-80;bj_view_y=y-64;render();
    }
}
void bj_view_close(void) BANKED {bj_view_active=0;ui_set_pos(0,144);}
