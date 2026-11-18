"""Original, exact-pixel tanker artwork. No external artwork or game assets."""
from PIL import Image, ImageDraw, ImageColor
from pathlib import Path
import json, hashlib, uuid
ROOT=Path(__file__).resolve().parents[1]
SRC=[ImageColor.getrgb(c) for c in ['#e0f8cf','#86c06c','#306850','#071821']]
PAL=[['CBD9D4','74999D','345462','102330'],['ABBAB7','66828A','314A58','101D2A'],['FBE7A1','E8A951','80513B','292D38'],['96B9BA','52787D','263D4B','101B28'],['B6DBCF','65B8AD','326C72','163A48'],['D7AA7A','A36C4D','674238','302C34'],['CFDADA','7C9A9C','405966','1C2B38']]
def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'dead-drop/'+s))
def write(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,indent=2)+'\n')
def rle(a):
 out='';last=a[0];n=0
 for v in a:
  if v!=last:out+=f'{last:02x}{n:x}+';last=v;n=0
  n+=1
 return out+f'{last:02x}{n:x}+'
font=Image.open(ROOT/'assets/fonts/bench-mono.png').convert('RGB')
def label(im,xy,text,color=0,scale=1):
 x,y=xy
 for c in text:
  k=max(0,ord(c)-32);g=font.crop(((k%16)*8,(k//16)*8,(k%16)*8+8,(k//16)*8+8))
  for yy in range(7):
   for xx in range(6):
    if g.getpixel((xx,yy))[1]<180:
     ImageDraw.Draw(im).rectangle((x+xx*scale,y+yy*scale,x+(xx+1)*scale-1,y+(yy+1)*scale-1),fill=SRC[color])
  x+=6*scale
T={}
def tile(name,rows):
 im=Image.new('RGB',(8,8));im.putdata([SRC[int(c)] for row in rows for c in row]);T[name]=im
# Patterns are hand-authored in four native source shades.
tile('plate',['22222223','21222223','22222223','22222223','22222223','22222223','22222213','33333333'])
tile('grate',['33333333','21212123','23232323','21212123','23232323','21212123','23232323','33333333'])
tile('dark',['33333333','32333333','33333333','33333333','33333333','33333333','33333323','33333333'])
tile('wall',['11111111','00000000','22222222','21111212','23333232','22222222','33333333','33333333'])
tile('rail',['33333333','11111111','33333333','23333323','23333323','23333323','23333323','33333333'])
tile('water',['33333333','33222233','33333333','33333332','22333333','33333333','33322333','33333333'])
tile('hazard',['11003311','10033110','00331100','03311003','33110033','31100331','11003311','10033110'])
tile('pipe',['33211333','33201333','33201333','33100133','33211333','33201333','33201333','33211333'])
tile('crate',['00000003','01222213','02122123','02211223','02211223','02122123','01222213','33333333'])
tile('vent',['11111113','12222223','13333323','12222223','13333323','12222223','13333323','33333333'])
tile('lamp',['33333333','32111123','31000013','31000013','32111123','33322333','33222233','32222223'])
tile('screen',['11111113','13333313','13000313','13222313','13003313','13333313','11111113','33333333'])
tile('machine',['00000003','01222213','02333223','02313223','02333223','02222223','01111113','33333333'])
tile('door',['00111100','01222210','01211210','01200210','01200210','01211210','01222210','00111100'])
tile('arrow',['33303333','33000333','30000033','33303333','33303333','33303333','33303333','33333333'])
tile('plain',['22222222']*8)
tile('seam',['22222223','22222223','22222223','22222223','22222223','22222223','22222223','33333333'])
names=['BOARDING PLATFORM','AFT WINCH DECK','CONTAINER SPINE','CUSTOMS LOCK','CREW PASSAGE','MESS HALL','SECURITY OFFICE','SERVICE TRUNK','BALLAST GALLERY','PUMP CONTROL','ENGINE ROOM','GENERATOR','LOWER HOLD','TANK CATWALK','SIGNAL ARCHIVE','RADIO ROOM','OFFICER QUARTERS','BRIDGE','CIPHER VAULT','MISSILE CARGO','LAUNCH CONTROL','FOREDECK','CRANE GANTRY','LIFEBOAT','INFIRMARY','ARMORY','CHART ROOM','VENTILATION']
allrooms=[]
for n,name in enumerate(names):
 w,h=40,36;im=Image.new('RGB',(w*8,h*8),SRC[3]);attrs=[0]*(w*h);cols=[0]*(w*h)
 exterior=n in [0,1,2,13,21,22,23]
 floorpal=0 if exterior else (5 if n in [9,10,11,19] else 1)
 def put(x,y,t,p=floorpal,col=0):
  if 0<=x<w and 0<=y<h:im.paste(T[t],(x*8,y*8));attrs[y*w+x]=p;cols[y*w+x]=col
 def rect(x,y,ww,hh,t,p=floorpal,col=0):
  for yy in range(y,y+hh):
   for xx in range(x,x+ww):put(xx,yy,t,p,col)
 for y in range(h):
  for x in range(w):put(x,y,'plate' if x%4==0 and y%4==0 else 'grate' if x in [10,11] else 'seam' if y%4==3 else 'plain')
 rect(0,0,w,2,'water' if exterior else 'wall',3,15);rect(0,h-2,w,2,'water' if exterior else 'wall',3,15)
 rect(0,0,2,h,'water' if exterior else 'wall',3,15);rect(w-2,0,2,h,'water' if exterior else 'wall',3,15)
 rect(2,2,1,32,'rail' if exterior else 'pipe',6,15);rect(37,2,1,32,'rail' if exterior else 'pipe',6,15)
 # Shadow routes occupy dark textured bays. Collision bit 0x10 is stealth shade.
 for x,y,ww,hh in [(3,24,12,8),(26,12,11,8),(3,3,12,6)]:rect(x,y,ww,hh,'dark',3,16)
 # Two transverse bulkheads create long, legible loops with vent alternatives.
 rect(3,10,28,2,'crate' if n%3==2 else 'wall',5 if n%3==2 else 6,15)
 rect(10,21,27,2,'machine' if n%4==2 else 'wall',6,15)
 rect(31,10,6,1,'hazard',2);rect(3,21,7,1,'hazard',2)
 # Crouch-only grated cut-throughs are fast but expose you to sightlines.
 if n in [2,4,7,8,12,16,22,27]:rect(6,10,3,2,'grate',3,32)
 if n in [1,4,7,13,16,21,27]:rect(31,21,3,2,'grate',3,32)
 # Cover modules, never on the two main passages.
 for k,(x,y) in enumerate([(17,27),(25,28),(12,15),(20,16),(24,4),(16,5)]):
  rect(x,y,3+(n+k)%2,2+(k%2),'crate' if (n+k)%3 else 'machine',5 if (n+k)%3 else 4,15)
  rect(x,y+3,4,1,'dark',3,16)
 # Pipelines, equipment, light pools and sector stencilling.
 for x,y in [(33,7),(5,18),(33,30)]:put(x,y,'lamp',2)
 for y in range(3,34):
  if cols[y*w+35]==0:put(35,y,'seam',2)
 # North and south hatches. East/west side route hatches added by scene generator.
 rect(29,2,5,2,'door',4);rect(4,32,5,2,'door',4)
 put(31,4,'arrow',4);put(6,31,'arrow',4)
 label(im,(32,24),f'{n+1:02d} / '+name[:17],0)
 for xx in range(4,20):attrs[3*w+xx]=6
 # Central interactable terminal matches a native actor at 29,6.
 rect(29,6,2,2,'screen',4,0)
 label(im,(30*8,9*8),'A',0);attrs[9*w+30]=4
 # Room-specific large machinery to make the silhouettes distinct.
 if n in [8,9,10,11,13,19]:
  rect(17,26,6,4,'pipe' if n%2 else 'machine',5,15)
 if n in [4,5,16,24]:rect(12,15,6,3,'vent',6,15)
 if n in [14,15,17,18,20,26]:
  rect(16,5,5,2,'screen',4,15)
 # A different central silhouette identifies each part of the ship.
 # These set pieces sit inside a shared navigable ring, with authored cover.
 hero=['cable','winch','containers','inspection','ducts','tables','monitors','pipes','tanks','pumps','turbine','generator','cargo','tanks','servers','antenna','bunks','bridge','servers','missiles','monitors','hull','crane','lifeboat','beds','weapons','chart','fans'][n]
 hx,hy=14,14;hw,hh=14,5
 rect(hx,hy,hw,hh,'plain',5 if n in [1,2,10,19,23] else 4,15)
 d=ImageDraw.Draw(im);x,y=hx*8,hy*8
 d.rectangle((x,y,x+111,y+39),fill=SRC[3]);d.line((x,y+39,x+111,y+39),fill=SRC[2])
 if hero in ['tanks','pumps','turbine','generator','fans','winch']:
  for ox in [2,39,76]:
   d.ellipse((x+ox,y+2,x+ox+31,y+33),fill=SRC[2],outline=SRC[0]);d.ellipse((x+ox+6,y+8,x+ox+25,y+27),fill=SRC[3],outline=SRC[1]);d.line((x+ox+15,y+9,x+ox+15,y+26),fill=SRC[1]);d.line((x+ox+7,y+18,x+ox+24,y+18),fill=SRC[1])
 elif hero in ['monitors','servers','bridge','inspection','chart']:
  for ox in range(3,105,21):
   d.rectangle((x+ox,y+3,x+ox+17,y+23),fill=SRC[2],outline=SRC[1]);d.rectangle((x+ox+2,y+5,x+ox+15,y+16),fill=SRC[3]);d.line((x+ox+4,y+12,x+ox+8,y+8,x+ox+13,y+10),fill=SRC[0]);d.rectangle((x+ox,y+28,x+ox+17,y+35),fill=SRC[1]);d.line((x+ox+2,y+31,x+ox+14,y+31),fill=SRC[3])
 elif hero in ['missiles','weapons']:
  for oy in [3,23]:
   d.polygon([(x+4,y+oy+6),(x+16,y+oy),(x+95,y+oy),(x+106,y+oy+6),(x+95,y+oy+12),(x+16,y+oy+12)],fill=SRC[1]);d.line((x+18,y+oy+4,x+88,y+oy+4),fill=SRC[0]);d.rectangle((x+30,y+oy,x+34,y+oy+12),fill=SRC[2]);d.rectangle((x+74,y+oy,x+78,y+oy+12),fill=SRC[2])
 elif hero in ['lifeboat','hull','cable','crane','antenna']:
  d.polygon([(x+2,y+19),(x+22,y+4),(x+91,y+4),(x+109,y+19),(x+91,y+35),(x+22,y+35)],fill=SRC[2],outline=SRC[0]);d.rectangle((x+25,y+10,x+86,y+29),fill=SRC[3]);d.line((x+55,y+10,x+55,y+29),fill=SRC[1]);d.line((x+25,y+19,x+86,y+19),fill=SRC[1])
 else:
  for ox in range(4,105,27):
   d.rectangle((x+ox,y+3,x+ox+20,y+33),fill=SRC[2],outline=SRC[1]);d.line((x+ox+4,y+7,x+ox+16,y+7),fill=SRC[0]);d.line((x+ox+4,y+13,x+ox+16,y+13),fill=SRC[1]);d.line((x+ox+4,y+20,x+ox+16,y+20),fill=SRC[1])
 label(im,(x+3,y+41),hero.upper(),0)
 for xx in range(hx,hx+hw):attrs[(hy+5)*w+xx]=6
 # Clearly marked side doors and supply destinations.
 if n in [4,5,6,16]:
  rect(35,27,2,4,'door',4);label(im,(28*8,26*8),'SIDE >',0)
 im.save(ROOT/f'assets/backgrounds/sector_{n:02d}.png')
 allrooms.append({'name':name,'collisions':rle(cols),'tileColors':rle(attrs),'id':uid(f'room/{n}'),'backgroundId':uid(f'bg/{n}')})
# Title: widescreen maritime silhouette, moon, waves, cranes and warning bars.
im=Image.new('RGB',(160,144),SRC[3]);d=ImageDraw.Draw(im)
for y in [2,9,17,26,37,113,119,128,137]:
 for x in range((y*7)%13,160,19):d.line((x,y,x+7,y),fill=SRC[2])
d.ellipse((119,12,139,32),fill=SRC[1]);d.ellipse((113,9,132,29),fill=SRC[3])
label(im,(18,39),'DEAD DROP',0,2);label(im,(29,61),'TANKER / 03:17',1)
d.polygon([(9,96),(137,96),(151,88),(144,109),(27,109)],fill=SRC[2]);d.line((12,95,145,95),fill=SRC[1])
for x in range(31,104,17):d.rectangle((x,84,x+14,94),fill=SRC[1]);d.line((x+4,85,x+4,93),fill=SRC[2]);d.line((x+10,85,x+10,93),fill=SRC[2])
d.rectangle((112,74,135,94),fill=SRC[2]);d.rectangle((119,67,132,74),fill=SRC[1]);d.rectangle((123,57,125,66),fill=SRC[2])
for x in range(115,134,5):d.rectangle((x,77,x+2,79),fill=SRC[0])
d.line((50,83,50,69,86,78),fill=SRC[1]);d.line((50,70,73,82),fill=SRC[2])
label(im,(35,121),'PRESS START',0);label(im,(26,134),'A STEALTH OPERATION',1)
im.save(ROOT/'assets/backgrounds/title.png')
# Deliberately drawn animated sprites: down, up and right, two frames each.
spy=["................","......3333......",".....322223.....",".....310013.....",".....333333.....","......3223......","....33222333....","...3222222223...","...3232222323...","...3332222333...",".....322223.....",".....333333.....",".....32..23.....",".....32..23.....","....333..333....","................"]
guard=["................",".....333333.....","....32222223....","....33333333....",".....310013.....",".....322223.....","....33333333....","...3212222123...","...3232222323...","...3332222333...",".....321123.....",".....333333.....",".....32..23.....",".....32..23.....","....333..333....","................"]
for kind,pattern in [('operative',spy),('sentry',guard)]:
 sheet=Image.new('RGB',(96,16),'#65ff00')
 for facing in range(3):
  for step in range(2):
   frame=[list(r) for r in pattern]
   if facing==1:
    frame[3]=list('.....322223.....');frame[4]=list('.....322223.....');frame[8]=list('...3233333323...')
   if facing==2:
    frame[3]=list('......31003.....');frame[8]=list('....32222223333.');frame[9]=list('....32222223333.')
   if step:
    frame[13]=list('....32....23....');frame[14]=list('...333....333...')
   for y,row in enumerate(frame):
    for x,c in enumerate(row):
     if c!='.':sheet.putpixel((facing*32+step*16+x,y), {'0':SRC[0],'1':SRC[0],'2':SRC[1],'3':SRC[3]}[c])
 sheet.save(ROOT/f'assets/sprites/{kind}.png')
# Dotted sight direction marker, terminal and projectile.
for name in ['sight','terminal','tracer']:
 sheet=Image.new('RGB',(48 if name=='sight' else 16,16),'#65ff00');d=ImageDraw.Draw(sheet)
 if name=='sight':
  for direction in range(3):
   points=[(7,3),(6,6),(8,6),(5,9),(9,9),(4,12),(10,12)]
   for x,y in points:
    if direction==1:y=15-y
    if direction==2:x,y=y,x
    d.point((direction*16+x,y),fill=SRC[1])
 elif name=='terminal':
  d.rectangle((2,2,13,13),fill=SRC[3]);d.rectangle((3,3,12,9),fill=SRC[1]);d.line((5,5,10,5),fill=SRC[0]);d.point((11,12),fill=SRC[0])
 else:d.line((5,8,10,8),fill=SRC[0]);d.point((8,7),fill=SRC[1])
 sheet.save(ROOT/f'assets/sprites/{name}.png')
# HUD font packed as 2bpp, dedicated to the engine's CGB UI tile region.
fontbytes=[]
for k in range(64):
 for y in range(8):
  bits=0
  for x in range(8):
   rgb=font.getpixel(((k%16)*8+x,(k//16)*8+y));bits|=(1 if rgb[1]<180 else 0)<<(7-x)
  fontbytes.extend([255^bits,255^bits])
(ROOT/'plugins/dead-drop/engine/include/dd_font.h').write_text('static const unsigned char dd_font[1024] = {\n'+','.join(map(str,fontbytes))+'\n};\n')
write(ROOT/'design/rooms.json',allrooms)
for i,p in enumerate(PAL):write(ROOT/f'project/palettes/tanker_{i}.gbsres',{'_resourceType':'palette','id':uid(f'palette/{i}'),'name':['Cold steel','Interior','Sodium lamps','Deep shadow','CRT mint','Oxide cargo','Stencils'][i],'colors':p})
print('Authored 29 backgrounds, five sprite sheets, seven palettes and the HUD font.')

# Keep expanded combat sheets in sync when rebuilding the base artwork.
import runpy
runpy.run_path(str(ROOT / "tools/author_combat.py"))
