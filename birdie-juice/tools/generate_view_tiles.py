"""Original 2bpp close-up terrain tiles; six palettes, sixteen edge masks each."""
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'plugins/birdie-golf/engine/src/core/birdie_view_tiles.c'
data=[]
for terrain in range(6):
 for mask in range(16):
  for y in range(8):
   lo=hi=0
   for x in range(8):
    inside=mask & (1<<((y//4)*2+x//4))
    v=(0 if terrain in (1,2,3) else 1) if inside else (2 if terrain in (1,4) else 3)
    if inside:
     if terrain==0 and (x,y) in [(1,2),(5,6)]:v=2
     if terrain==1 and (x+y//2)%8<3:v=1
     if terrain==2 and (x,y)==(2,2):v=1
     if terrain==3 and (x,y) in [(2,5),(6,1)]:v=1
     if terrain==4 and y==3 and x in (2,3,4):v=0
     if terrain==5:v=3 if y>5 or abs(x-4)>y//2 else 1
    lo=lo*2+(v&1);hi=hi*2+(v>>1)
   data.extend((lo,hi))
out.write_text('#pragma bank 255\n#include "states/golf.h"\nstatic const UBYTE tiles[]={'+','.join(map(str,data))+'};\nvoid bj_view_tiles(void) BANKED {VBK_REG=1;set_bkg_data(0,96,tiles);VBK_REG=0;}\n')

# Flowing diagonal chevrons: a four-phase sequence shared by all green tiles.
flow=[]
for phase in range(4):
 for offset in range(4):
  shift=(phase+offset)%4
  for y in range(8):
   lo=hi=0
   for x in range(8):
    v=1 if (x,y)==(0,0) else 0
    if (x,y) in [((a+shift)%8,(b+shift)%8) for a,b in [(1,1),(2,2),(3,3),(1,3),(2,3),(3,1),(3,2)]]:v=3
    lo=lo*2+(v&1);hi=hi*2+(v>>1)
   flow.extend((lo,hi))
with out.open('a') as f:
 f.write('#include "game_time.h"\nstatic const UBYTE flow[]={'+','.join(map(str,flow))+'};\nvoid bj_view_grid(void) BANKED {VBK_REG=1;set_bkg_data(96,4,flow+((game_time>>4)&3)*64);VBK_REG=0;}\n')
