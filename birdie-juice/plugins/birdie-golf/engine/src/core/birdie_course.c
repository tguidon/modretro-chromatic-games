#pragma bank 255
#include <string.h>
#include "states/golf.h"
UBYTE bj_terrain_1(UWORD cell) BANKED;
UBYTE bj_terrain_2(UWORD cell) BANKED;
UBYTE bj_terrain_3(UWORD cell) BANKED;
UBYTE bj_terrain_4(UWORD cell) BANKED;
UBYTE bj_terrain_5(UWORD cell) BANKED;
UBYTE bj_terrain_6(UWORD cell) BANKED;
UBYTE bj_terrain_7(UWORD cell) BANKED;
UBYTE bj_terrain_8(UWORD cell) BANKED;
UBYTE bj_terrain_9(UWORD cell) BANKED;
static const bj_hole_t bj_holes[9]={{4,36,116,116,36,"MORNING DEW",3,1,1,1},{3,44,116,108,44,"SHORT SQUEEZE",-2,1,-1,1},{5,36,116,124,36,"DOGLEG PUNCH",2,-2,1,1},{4,116,116,44,36,"SAND WEDGE",-3,-1,-1,1},{4,36,116,116,36,"CREEKSIDE",2,2,1,1},{3,44,116,100,44,"ISLAND LIME",-2,-1,-1,1},{5,20,116,132,28,"LONG POUR",3,-1,1,1},{4,116,116,36,36,"ORCHARD RUN",-2,2,-1,1},{4,36,116,108,36,"LAST CALL",1,-3,1,1}};
void bj_read_hole(UBYTE hole,bj_hole_t *dest) BANKED {memcpy(dest,&bj_holes[hole],sizeof(bj_hole_t));}
UBYTE bj_terrain(UBYTE hole,UBYTE x,UBYTE y) BANKED {UWORD cell;if(x>=160||y<16||y>=128)return BJ_WATER;cell=((UWORD)((y-16)>>1))*80+(x>>1);switch(hole){case 0:return bj_terrain_1(cell);case 1:return bj_terrain_2(cell);case 2:return bj_terrain_3(cell);case 3:return bj_terrain_4(cell);case 4:return bj_terrain_5(cell);case 5:return bj_terrain_6(cell);case 6:return bj_terrain_7(cell);case 7:return bj_terrain_8(cell);case 8:return bj_terrain_9(cell);}return BJ_WATER;}
