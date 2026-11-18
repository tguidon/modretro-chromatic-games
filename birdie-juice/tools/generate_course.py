"""Build native course assets/resources from course/holes.json. Requires Pillow."""
import json, uuid, itertools
from pathlib import Path
from PIL import Image, ImageDraw
from course_art import PALETTES, draw_course
ROOT=Path(__file__).resolve().parents[1]
def uid(name): return str(uuid.uuid5(uuid.NAMESPACE_URL,'birdie-juice/'+name))
def write(path,data):
    path=ROOT/path;path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists() and path.suffix == '.gbsres':
        old=json.loads(path.read_text())
        # Keep editor scripts, IDs and unknown fields when regenerating authored art.
        if data.get('_resourceType') in ('scene','actor'):
            for key in ('id','script','startScript','updateScript','playerHit1Script','playerHit2Script','playerHit3Script','hit1Script','hit2Script','hit3Script','collisions'):
                if key in old: data[key]=old[key]
        data={**old,**data}
    path.write_text(json.dumps(data,indent=2)+'\n')
def pack(values):
    return ''.join(f'{v:02x}'+('!' if len(g)==1 else f'{len(g):x}+') for v,group in itertools.groupby(values) for g in [list(group)])
course=json.loads((ROOT/'course/holes.json').read_text())
assert len(course['holes'])==9 and sum(h['par'] for h in course['holes'])==36
assert sorted(h['par'] for h in course['holes'])==[3,3,4,4,4,4,4,5,5]
if not (ROOT/'project.gbsproj').exists(): write(Path('project.gbsproj'),{'_resourceType':'project','name':'Birdie Juice','author':'tguidon','notes':'Nine-hole golf. Par 36. Game rules: plugins/birdie-golf. Course source: course/holes.json.','_version':'4.2.0','_release':'10'})
palettes=PALETTES
for name,colors in palettes: write(Path(f'project/palettes/{name}.gbsres'),{'_resourceType':'palette','id':name,'name':name.title(),'colors':colors,'defaultName':name,'defaultColors':colors})
settings=json.loads((ROOT/'project/settings.gbsres').read_text())
settings.update(startSceneId=uid('hole1'),startX=4,startY=14,startDirection='up',defaultBackgroundPaletteIds=[p[0] for p in palettes[:6]]+['sky','default-ui'],defaultSpritePaletteIds=['sprite']*8,defaultSpritePaletteId='sprite',playerPaletteId='sprite',defaultUIPaletteId='default-ui',defaultPlayerSprites={'GOLF':uid('ball')},defaultSceneTypeId='GOLF',colorMode='color',romFilename='birdie-juice',generateDebugFilesEnabled=True,showConnections=True)
write(Path('project/settings.gbsres'),settings)

# Explicit 5x7 glyphs. HUD uses its own reserved 64-tile font, independent of dialogue.
patterns={
'0':'0E11131519110E','1':'040C040404040E','2':'0E11010204081F','3':'1E01010E01011E','4':'02060A121F0202','5':'1F10101E01011E','6':'0E10101E11110E','7':'1F010204080808','8':'0E11110E11110E','9':'0E11110F01010E',
'A':'0E11111F111111','B':'1E11111E11111E','C':'0E11101010110E','D':'1E11111111111E','E':'1F10101E10101F','F':'1F10101E101010','G':'0E11101711110F','H':'1111111F111111','I':'0E04040404040E','J':'0702020212120C','K':'11121418141211','L':'1010101010101F','M':'111B1515111111','N':'11191513111111','O':'0E11111111110E','P':'1E11111E101010','Q':'0E11111115120D','R':'1E11111E141211','S':'0F10100E01011E','T':'1F040404040404','U':'1111111111110E','V':'11111111110A04','W':'11111115151B11','X':'11110A040A1111','Y':'11110A04040404','Z':'1F01020408101F',
'^':'040A1100000000','-':'0000001F000000','+':'0004041F040400',':':'00040000040000','/':'01010204081010','>':'10080402040810','<':'01020408040201','.':'00000000000C0C','!':'04040404040004','%':'11120204080911','[':'0E08080808080E',']':'0E02020202020E','=':'00001F001F0000','?':'0E110204040004'}
font=[]
for n in range(32,96):
    rows=bytes.fromhex(patterns.get(chr(n),'00000000000000'))
    for y in range(8):
        bits=(rows[y]<<2) if y<7 else 0
        font.extend([bits,bits])
engine=ROOT/'plugins/birdie-golf/engine'
fontstr=','.join(str(x) for x in font)
(engine/'src/core/birdie_font.c').write_text('#pragma bank 255\n#include <gbdk/platform.h>\n#include "states/golf.h"\nstatic const UBYTE bj_font[]={'+fontstr+'};\nvoid bj_load_font(void) BANKED { VBK_REG=0; set_bkg_data(128,64,bj_font); }\n')
hole_c=[]
water_cells=[]
water_counts=[]
for i,h in enumerate(course['holes']):
    n=i+1
    image,attrs,terrain=draw_course(h)
    cells=[(x,y) for y in range(2,16) for x in range(20) if all(terrain.getpixel((px,py))==4 for py in range(y*8,y*8+8,2) for px in range(x*8,x*8+8,2))]
    water_counts.append(len(cells));water_cells.extend(v for cell in cells for v in cell)
    tx,ty=h['tee'];hx,hy=h['cup']
    assert terrain.getpixel((tx*8+4,ty*8+4))==1, (n,'tee must be fairway')
    assert terrain.getpixel((hx*8+4,hy*8+4))==2, (n,'cup must be on green')
    filename=f'hole_{n:02}.png';image.convert('RGB').save(ROOT/'assets/backgrounds'/filename)
    write(Path('assets/backgrounds')/(filename+'.gbsres'),{'_resourceType':'background','id':uid('bg'+str(n)),'name':f'{n:02} {h["name"]}','symbol':f'bg_hole_{n:02}','tileColors':pack(attrs),'filename':filename,'width':20,'height':18,'imageWidth':160,'imageHeight':144,'autoColor':False})
    scene={'_resourceType':'scene','id':uid('hole'+str(n)),'_index':i,'type':'GOLF','name':f'{n:02} {h["name"]} - Par {h["par"]}','symbol':f'scene_hole_{n:02}','x':i%3*240,'y':i//3*210,'width':20,'height':18,'backgroundId':uid('bg'+str(n)),'tilesetId':'','colorModeOverride':'none','paletteIds':[],'spritePaletteIds':['sprite']*8,'playerSpriteSheetId':uid('ball'),'autoFadeSpeed':1,'script':[],'playerHit1Script':[],'playerHit2Script':[],'playerHit3Script':[],'collisions':pack([0]*360),'notes':f'Tee {h["tee"]}, cup {h["cup"]}. Course data: course/holes.json. Rules: plugins/birdie-golf.'}
    folder=Path(f'project/scenes/hole_{n:02}')
    write(folder/'scene.gbsres',scene)
    for index,(kind,x,y) in enumerate([('aim',tx,ty),('golfer',tx-1,ty),('flag',hx,hy),('shadow',tx,ty)]):
        nxt=n%9+1;nx,ny=course['holes'][nxt-1]['tee']
        script=[{'id':uid('next'+str(n)),'command':'EVENT_SWITCH_SCENE','args':{'sceneId':uid('hole'+str(nxt)),'x':{'type':'number','value':nx},'y':{'type':'number','value':ny},'direction':'up','fadeSpeed':'2'}}] if kind=='aim' else []
        actor={'_resourceType':'actor','_index':index,'id':uid(f'{n}-{kind}'),'symbol':f'actor_{n:02}_{kind}','name':kind.title(),'prefabId':'','coordinateType':'tiles','x':x,'y':y,'frame':0,'animate':False,'spriteSheetId':uid(kind),'paletteId':'sprite','direction':'down','moveSpeed':1,'animSpeed':255,'isPinned':False,'persistent':True,'collisionGroup':'','collisionExtraFlags':[],'prefabScriptOverrides':{},'script':script,'startScript':[],'updateScript':[],'hit1Script':[],'hit2Script':[],'hit3Script':[]}
        write(folder/f'actors/{index+1:02}_{kind}.gbsres',actor)
    terrain.save(ROOT/f'course/art/hole_{n:02}_terrain.png')
    values=[terrain.getpixel((x,y)) for y in range(16,128,2) for x in range(0,160,2)]
    packed=[values[j]|(values[j+1]<<4) for j in range(0,len(values),2)]
    (engine/f'src/core/birdie_terrain_{n:02}.c').write_text('#pragma bank 255\n#include "states/golf.h"\nstatic const UBYTE map[]={'+','.join(map(str,packed))+'};\nUBYTE bj_terrain_'+str(n)+'(UWORD cell) BANKED {UBYTE value=map[cell>>1];return (cell&1)?value>>4:value&15;}\nvoid bj_row_'+str(n)+'(UBYTE row,UBYTE *dest) BANKED {UBYTE i;UWORD offset=(UWORD)row*40;for(i=0;i<40;i++)dest[i]=map[offset+i];}\n')
    wind=h.get('wind',[(n%3)-1,-2+(n%3)])
    slope=h.get('slope',[1 if n%2 else -1,1])
    hole_c.append('{'+f'{h["par"]},{tx*8+4},{ty*8+4},{hx*8+4},{hy*8+4},"{h["name"].upper()}",'+','.join(map(str,wind+slope))+'}')
terrain_api=''.join(f'UBYTE bj_terrain_{n}(UWORD cell) BANKED;\nvoid bj_row_{n}(UBYTE row,UBYTE *dest) BANKED;\n' for n in range(1,10))
terrain_switch=''.join(f'case {n-1}:return bj_terrain_{n}(cell);' for n in range(1,10))
(engine/'src/core/birdie_course.c').write_text('#pragma bank 255\n#include <string.h>\n#include "states/golf.h"\n'+terrain_api+'static const bj_hole_t bj_holes[9]={'+','.join(hole_c)+'};\nvoid bj_read_hole(UBYTE hole,bj_hole_t *dest) BANKED {memcpy(dest,&bj_holes[hole],sizeof(bj_hole_t));}\nUBYTE bj_terrain(UBYTE hole,UBYTE x,UBYTE y) BANKED {UWORD cell;if(x>=160||y<16||y>=128)return BJ_WATER;cell=((UWORD)((y-16)>>1))*80+(x>>1);switch(hole){'+terrain_switch+'}return BJ_WATER;}\n')

with (engine/'src/core/birdie_course.c').open('a') as file:
    file.write('void bj_terrain_row(UBYTE hole,INT16 y,UBYTE *dest) BANKED {UBYTE row;if(y<16||y>=128){memset(dest,0,40);return;}row=(y-16)>>1;switch(hole){'+''.join(f'case {n-1}:bj_row_{n}(row,dest);break;' for n in range(1,10))+'}}\n')

offsets=[];offset=0
for count in water_counts:offsets.append(offset);offset+=count*2
(engine/'src/core/birdie_water.c').write_text('#pragma bank 255\n#include "states/golf.h"\nstatic const UBYTE cells[]={'+','.join(map(str,water_cells))+'};\nstatic const UWORD offsets[]={'+','.join(map(str,offsets))+'};\nstatic const UBYTE counts[]={'+','.join(map(str,water_counts))+'};\nvoid bj_water_init(void) BANKED {UBYTE i,x,y,tile,attr=12;UWORD p=offsets[bj_hole];for(i=0;i<counts[bj_hole];i++){x=cells[p++];y=cells[p++];tile=100+((x+y)&3);VBK_REG=0;set_bkg_tiles(x,y,1,1,&tile);VBK_REG=1;set_bkg_tiles(x,y,1,1,&attr);}VBK_REG=0;bj_water_tiles();}\n')

# Transparent green is GB Studio's native sprite key. The other colors map to sprite indices 1..3.
for kind in ['ball','aim','golfer','flag','shadow']:
    im=Image.new('RGB',(16,16),'#00ff00');p=ImageDraw.Draw(im)
    if kind=='shadow':
        p.line((6,10,10,10),fill='#000000');p.line((7,9,9,9),fill='#000000')
    elif kind=='ball':
        p.ellipse((6,7,10,10),fill='#000000');p.rectangle((7,7,9,9),fill='#ffffff');p.point((7,7),fill='#aaaaaa')
    elif kind=='aim':
        p.line((4,8,6,8),fill='#ffffff');p.line((10,8,12,8),fill='#ffffff');p.line((8,4,8,6),fill='#ffffff');p.line((8,10,8,12),fill='#ffffff');p.point((8,8),fill='#000000')
    elif kind=='flag':
        p.line((8,1,8,9),fill='#000000');p.polygon([(9,1),(14,3),(9,5)],fill='#aaaaaa');p.line((7,9,10,9),fill='#000000')
    else:
        p.ellipse((4,12,12,14),fill='#000000');p.rectangle((6,8,10,11),fill='#aaaaaa');p.rectangle((6,4,10,7),fill='#ffffff');p.rectangle((5,3,11,4),fill='#ffffff');p.line((7,12,6,14),fill='#ffffff');p.line((10,12,11,14),fill='#ffffff');p.line((11,9,14,12),fill='#000000');p.line((13,12,15,12),fill='#ffffff')
    frames=[im]
    if kind=='flag':
        cup=Image.new('RGB',(16,16),'#00ff00');q=ImageDraw.Draw(cup)
        q.ellipse((5,7,11,11),fill='#ffffff');q.ellipse((6,8,10,10),fill='#000000');frames.append(cup)
    if kind=='ball':
        for size in (2,1):
            dot=Image.new('RGB',(16,16),'#00ff00');q=ImageDraw.Draw(dot)
            q.rectangle((8,8,8+size-1,8+size-1),fill='#ffffff');frames.append(dot)
    if kind=='golfer':
        for style in range(3):
            effect=Image.new('RGB',(16,16),'#00ff00');q=ImageDraw.Draw(effect)
            color='#aaaaaa' if style==0 else '#ffffff'
            for x,y in [(2,6),(5,3),(10,4),(13,7),(4,10),(11,11)]:
                q.line((x,y,x+(1 if x>8 else -1),y-2-style),fill=color)
            q.arc((3,7,13,13),0,180,fill='#000000');frames.append(effect)
        guide=Image.new('RGB',(16,16),'#00ff00');q=ImageDraw.Draw(guide)
        q.rectangle((7,8,8,9),fill='#ffffff');frames.append(guide)
    if kind=='aim':
        frames=[]
        for radius in (4,7):
            ring=Image.new('RGB',(16,16),'#00ff00');q=ImageDraw.Draw(ring)
            q.ellipse((8-radius,8-radius,8+radius,8+radius),outline='#ffffff')
            q.line((6,8,10,8),fill='#000000');q.line((8,6,8,10),fill='#000000')
            frames.append(ring)
    if kind=='flag':
        alt=im.copy();q=ImageDraw.Draw(alt)
        q.rectangle((9,0,15,7),fill='#00ff00');q.polygon([(9,1),(14,1),(12,4),(9,5)],fill='#aaaaaa')
        frames.insert(1,alt)
    sheet=Image.new('RGB',(16*len(frames),16),'#00ff00')
    for f,frame in enumerate(frames):sheet.paste(frame,(f*16,0))
    name=f'{kind}.png';sheet.save(ROOT/'assets/sprites'/name)
    tiledata=[{'id':uid(kind+'tile'+str(x)),'x':x,'y':0,'sliceX':x,'sliceY':0,'flipX':False,'flipY':False,'palette':0,'paletteIndex':0,'objPalette':'OBP0','priority':False} for x in [0,8]]
    animations=[{'id':uid(kind+'anim'+str(a)),'frames':[{'id':uid(kind+'frame'+str(a)), 'tiles':tiledata if a==0 else []}]} for a in range(8)]
    for frame_index in range(1,len(frames)):
        animations[0]['frames'].append({'id':uid(kind+'-frame-'+str(frame_index)), 'tiles':[{**tile,'id':uid(kind+'-frame-'+str(frame_index)+'-'+str(tile['x'])),'sliceX':tile['sliceX']+16*frame_index} for tile in tiledata]})


    metadata={'_resourceType':'sprite','id':uid(kind),'name':kind.title(),'symbol':'sprite_'+kind,'states':[{'id':uid(kind+'state'),'name':'','animationType':'fixed','flipLeft':False,'animations':animations}],'numTiles':4,'canvasOriginX':0,'canvasOriginY':0,'canvasWidth':16,'canvasHeight':16,'boundsX':6,'boundsY':-2,'boundsWidth':4,'boundsHeight':4,'animSpeed':255,'filename':name,'width':sheet.width,'height':16}
    write(Path('assets/sprites')/(name+'.gbsres'),metadata)
# Store terrain additions back in the source, keeping future generation deterministic.
write(Path('course/holes.json'),course)
print('Generated 9 native scenes, 9 backgrounds, 5 sprites. PAR 36.')
