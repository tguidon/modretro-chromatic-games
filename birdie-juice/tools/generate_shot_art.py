"""Original native shot-camera artwork, packed into a reserved CGB VRAM bank."""
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'plugins/birdie-golf/engine/src/core/birdie_shot_art.c'
im=Image.new('L',(160,96),0);d=ImageDraw.Draw(im)
attrs=[]
# Sky, snow-capped ridge, layered conifers, then a receding fairway.
for ty in range(12):
    for tx in range(20):
        attrs.append((6 if ty<5 else 0 if ty<7 else 1 if ty<9 else 5)|8)
d.rectangle((0,0,159,39),fill=1)
for x,y in [(10,4),(87,8),(132,1)]:
    d.rectangle((x,y+5,x+22,y+8),fill=0)
    d.ellipse((x+3,y,x+13,y+9),fill=0);d.ellipse((x+11,y+2,x+19,y+9),fill=0)
for x,height in [(-12,20),(20,30),(62,24),(104,31),(144,19)]:
    peak=x+20;top=40-height
    d.polygon([(x-5,39),(peak,top),(x+45,39)],fill=2)
    d.polygon([(peak,top),(peak+4,39),(x+45,39)],fill=3)
    d.polygon([(peak,top),(peak-8,top+10),(peak-3,top+8),(peak+1,top+13),(peak+3,top+8),(peak+9,top+12)],fill=0)
d.rectangle((0,40,159,55),fill=1)
for x in range(-4,160,12):
    d.polygon([(x+6,40),(x+12,52),(x,52)],fill=2)
for x in range(-9,160,16):
    d.polygon([(x+7,41),(x+13,49),(x+11,49),(x+16,55),(x,55),(x+4,49),(x+1,49)],fill=3)
    d.line((x+7,43,x+3,49),fill=0);d.line((x+7,47,x+4,52),fill=1)
for y in range(56,96):
    edge=max(0,64-(y-56)*3)
    for x in range(160):
        if y<72:
            v=(0 if ((x+y//4)//12)%2 else 1) if edge<x<150-edge else 2
            if (x%8,y%8) in [(1,2),(5,6)]:v=min(3,v+1)
        else:
            v=3 if (x%8,y%8) in [(1,2),(5,6)] else 0
        im.putpixel((x,y),v)
# A low bunker and the distant pin give the shot view depth.
d.ellipse((112,59,144,65),fill=0);d.line((115,65,139,65),fill=3)
d.line((88,44,88,57),fill=3);d.polygon([(89,44),(96,46),(89,49)],fill=0)

def pack_tile(tile):
    data=[]
    for y in range(8):
        lo=hi=0
        for x in range(8):
            v=tile.getpixel((x,y));lo=(lo<<1)|(v&1);hi=(hi<<1)|((v>>1)&1)
        data.extend([lo,hi])
    return bytes(data)

def tiles(image):
    return [pack_tile(image.crop((x,y,x+8,y+8))) for y in range(0,image.height,8) for x in range(0,image.width,8)]
unique=[];tilemap=[]
for t in tiles(im):
    if t not in unique:unique.append(t)
    tilemap.append(unique.index(t))
assert len(unique)<=109,len(unique)
# Four deliberate poses, rendered into a 32x32 reserved patch at (32,72).
poses=[]
for pose in range(4):
    p=Image.new('L',(32,32),0);a=ImageDraw.Draw(p)
    a.ellipse((5,28,25,31),fill=3)
    a.polygon([(10,20),(16,20),(14,28),(9,28)],fill=3)
    a.polygon([(17,20),(21,20),(24,28),(19,28)],fill=3)
    a.rectangle((7,28,14,29),fill=1);a.rectangle((19,28,25,29),fill=1)
    a.polygon([(10,12),(18,11),(22,21),(10,22)],fill=3)
    a.polygon([(11,13),(17,12),(20,20),(11,20)],fill=2)
    a.rectangle((12,5,19,11),fill=3);a.rectangle((14,6,20,10),fill=1)
    a.point((19,7),fill=3);a.line((17,11,19,11),fill=3)
    a.polygon([(10,5),(12,2),(18,2),(21,5)],fill=2);a.line((10,5,23,5),fill=3)
    arms=[[(17,14),(21,19),(25,21)],[(17,14),(13,9),(7,5)],[(17,14),(24,11),(29,4)],[(17,14),(15,8),(24,3)]][pose]
    a.line(arms,fill=3,width=3);a.line(arms,fill=1)
    end=arms[-1]
    club=[(30,28),(3,0),(29,1),(30,8)][pose]
    a.line((end,club),fill=3);a.rectangle((max(0,club[0]-3),club[1],club[0],min(31,club[1]+2)),fill=1)
    if pose<2:a.rectangle((29,28,30,29),fill=1)
    poses.append(p)
# Retain source sheets for edits and review; these are not standalone GB Studio backgrounds.
art=ROOT/'course/art';art.mkdir(exist_ok=True)
im.point(lambda v: [255,170,85,0][v%4]).convert('RGB').save(art/'shot-panorama.png')
sheet=Image.new('L',(128,32))
for i,p in enumerate(poses):sheet.paste(p,(i*32,0))
sheet.point(lambda v: [255,170,85,0][v%4]).convert('RGB').save(art/'swing-poses.png')
def array(name, data):return 'static const UBYTE '+name+'[]={'+','.join(map(str,data))+'};\n'
code='#pragma bank 255\n#include "states/golf.h"\n#include "ui.h"\n'
code+=array('panorama',b''.join(unique))+array('panorama_map',tilemap)+array('panorama_attrs',attrs)
for i,p in enumerate(poses):code+=array('pose_'+str(i),b''.join(tiles(p)))
code+='''void bj_shot_pose(UBYTE pose) BANKED {
    static const UBYTE map[16]={112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127};
    static const UBYTE attrs[16]={13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13};
    VBK_REG=1;
    switch(pose) {case 0:set_bkg_data(112,16,pose_0);break;case 1:set_bkg_data(112,16,pose_1);break;case 2:set_bkg_data(112,16,pose_2);break;default:set_bkg_data(112,16,pose_3);}
    set_win_tiles(4,9,4,4,attrs);VBK_REG=0;set_win_tiles(4,9,4,4,map);
}
void bj_shot_art(void) BANKED {
'''
code+=f'    VBK_REG=1;set_bkg_data(0,{len(unique)},panorama);\n'
code+='    set_win_tiles(0,2,20,12,panorama_attrs);VBK_REG=0;set_win_tiles(0,2,20,12,panorama_map);bj_shot_pose(0);\n}\n'
OUT.write_text(code)
print(f'Shot camera: {len(unique)}/109 backdrop tiles + 3 meter + 16 pose tiles; bank 1 at 0x9000, separate from objects/HUD.')
