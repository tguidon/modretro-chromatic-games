#pragma bank 255
#include "states/golf.h"
static const UBYTE cells[]={1,8,13,8,17,8,5,5,5,6,9,4,9,5,2,8,3,8,4,8,5,8,14,8,15,8,16,8,9,2,8,3,8,4,15,4,8,5,15,5,10,7,12,7,13,7,10,10,11,10,10,11,11,11,13,4,14,4,13,5,14,5,4,7,5,7,4,8,5,8};
static const UWORD offsets[]={0,6,10,14,14,28,46,54,62};
static const UBYTE counts[]={3,2,2,0,7,9,4,4,4};
void bj_water_init(void) BANKED {UBYTE i,x,y,tile,attr=12;UWORD p=offsets[bj_hole];for(i=0;i<counts[bj_hole];i++){x=cells[p++];y=cells[p++];tile=100+((x+y)&3);VBK_REG=0;set_bkg_tiles(x,y,1,1,&tile);VBK_REG=1;set_bkg_tiles(x,y,1,1,&attr);}VBK_REG=0;bj_water_tiles();}
