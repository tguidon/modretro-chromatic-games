"""Append combat poses without altering the original walking frames or resource IDs."""
from pathlib import Path
from PIL import Image, ImageDraw
import json, uuid, hashlib
R=Path(__file__).resolve().parents[1];S=R/'assets/sprites';D=R/'design/combat';D.mkdir(parents=True,exist_ok=True)
T='#65ff00';K='#071821';M='#86c06c';W='#e0f8cf'
def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'dead-drop/combat/'+s))
def state(asset,name,row,palette):
 key=asset+'/'+name
 a=[]
 for index in range(8):
  tiles=[]
  if index in [0,2,3]:
   sx={0:32,2:16,3:0}[index]
   for half in range(2):tiles.append({'id':uid(f'{key}/{index}/{half}'),'x':half*8,'y':0,'sliceX':sx+half*8,'sliceY':row,'flipX':False,'flipY':False,'palette':0,'paletteIndex':palette,'objPalette':'OBP0','priority':False})
  a.append({'id':uid(f'{key}/anim/{index}'),'frames':[{'id':uid(f'{key}/frame/{index}'),'tiles':tiles}]})
 return {'id':uid(key),'name':name,'animationType':'multi','flipLeft':True,'animations':a}
def publish(name,baseheight,poses):
 p=S/f'{name}.png';meta=S/f'{name}.png.gbsres';v=json.loads(meta.read_text());base=Image.open(p).convert('RGB').crop((0,0,96 if name=='operative' else 16,baseheight))
 base.save(D/f'{name}-base.png')
 im=Image.new('RGB',(max(base.width,48),16*(len(poses)+1)),T);im.paste(base,(0,0))
 generated={n for n,_,_ in poses};v['states']=[s for s in v['states'] if s['name'] not in generated]
 for row,(n,frames,pal) in enumerate(poses,1):
  for facing,frame in enumerate(frames):im.paste(frame,(16*facing,16*row));frame.save(D/f'{name}-{row}-{facing}.png')
  v['states'].append(state(name,n,16*row,pal))
 im.save(p);v.update({'width':im.width,'height':im.height,'checksum':hashlib.sha1(p.read_bytes()).hexdigest()})
 # Exact source 8x16 pair estimate, excluding chroma-key-only pairs.
 pairs={im.crop((x,y,x+8,y+16)).tobytes() for y in range(0,im.height,16) for x in range(0,im.width,8)}
 pairs.discard(Image.new('RGB',(8,16),T).tobytes());v['numTiles']=len(pairs)
 meta.write_text(json.dumps(v,indent=2)+'\n')
base=Image.open(S/'operative.png').convert('RGB')
poses=[]
for phase,name in enumerate(['Pistol recoil','Knife windup','Knife sweep','Knife followthrough']):
 frames=[]
 for face,sx in enumerate([0,32,64]):
  f=base.crop((sx,0,sx+16,16));d=ImageDraw.Draw(f)
  # Keep legs/identity; replace only the arms and weapon silhouette.
  d.rectangle((2,6,13,10),fill=T);d.rectangle((5,6,10,10),fill=K);d.rectangle((6,6,9,10),fill=M)
  if face==2:
   if phase==0:
    d.line((7,7,11,6),fill=W,width=2);d.rectangle((10,5,15,7),fill=K);d.line((11,5,15,5),fill=W)
   elif phase==1:
    d.line((7,8,4,5),fill=M,width=2);d.line((4,5,7,2),fill=W,width=2)
   elif phase==2:
    d.line((8,8,13,8),fill=M,width=2);d.line((12,8,15,4),fill=W,width=2)
   else:
    d.line((8,8,12,11),fill=M,width=2);d.line((12,11,15,12),fill=W,width=2)
  else:
   up=face==1
   if phase==0:
    d.line((4,8,7,6 if up else 11),fill=M,width=2);d.line((11,8,8,6 if up else 11),fill=W,width=2)
    d.rectangle((7,0 if up else 10,8,5 if up else 15),fill=K);d.line((7,0 if up else 12,7,4 if up else 15),fill=W)
   elif phase==1:
    d.line((5,8,2,6),fill=M,width=2);d.line((2,6,3,2),fill=W,width=2)
   elif phase==2:
    d.line((9,8,12,5 if up else 10),fill=M,width=2);d.line((12,5 if up else 10,9,0 if up else 15),fill=W,width=2)
   else:
    d.line((9,8,13,8),fill=M,width=2);d.line((13,8,15,4 if up else 13),fill=W,width=2)
  frames.append(f)
 poses.append((name,frames,0))
publish('operative',16,poses)
fx=[]
for n in ['Pistol recoil','Pistol trail','Knife windup','Knife sweep','Knife followthrough','Impact spark']:
 f=Image.new('RGB',(16,16),T);d=ImageDraw.Draw(f)
 # Author facing right; rotate exact pixels for the vertical directions.
 if n=='Pistol recoil':
  d.polygon([(1,8),(6,5),(6,2),(9,6),(14,4),(12,8),(15,11),(9,10),(7,14),(6,10)],fill=M)
  d.polygon([(4,8),(8,5),(11,8),(8,11)],fill=W)
 elif n=='Pistol trail':
  d.line((0,7,12,7),fill=M,width=3);d.line((5,7,15,7),fill=W);d.point((14,6),fill=W)
 elif n=='Knife windup':
  d.line([(3,1),(8,1),(12,4)],fill=M,width=2);d.line([(5,0),(10,1),(13,4)],fill=W)
 elif n=='Knife sweep':
  d.line([(5,0),(11,2),(14,5),(15,8),(13,12),(9,15)],fill=M,width=3)
  d.line([(7,0),(12,3),(14,6),(14,9),(12,12),(8,15)],fill=W,width=2)
 elif n=='Knife followthrough':
  d.line([(13,7),(12,11),(9,14),(3,15)],fill=M,width=2);d.line([(14,9),(12,13),(7,15)],fill=W)
 else:
  d.line((2,2,5,5),fill=W,width=2);d.line((10,10,13,13),fill=W,width=2);d.line((2,13,5,10),fill=M,width=2);d.line((10,5,13,2),fill=M,width=2)
 fx.append((n,[f.transpose(Image.Transpose.ROTATE_270),f.transpose(Image.Transpose.ROTATE_90),f],2 if n.startswith('Pistol') else 0))
publish('tracer',16,fx)
engine=R/'plugins/dead-drop/engine/engine.json';v=json.loads(engine.read_text())
keys={'DD_POSE_SHOOT':'Pistol recoil','DD_FX_TRAIL':'Pistol trail','DD_POSE_WINDUP':'Knife windup','DD_POSE_SWEEP':'Knife sweep','DD_POSE_FOLLOW':'Knife followthrough','DD_FX_IMPACT':'Impact spark'}
v['fields']=[f for f in v['fields'] if f['key'] not in keys]+[{'key':k,'sceneType':'STEALTH','label':n,'group':'Dead Drop combat','type':'animationstate','cType':'define','defaultValue':n} for k,n in keys.items()]
engine.write_text(json.dumps(v,indent=2)+'\n')
(D/'timing.json').write_text(json.dumps({'pistol':{'duration':20,'muzzle_flash':[0,4],'trail':[5,19],'recoil_pose':[0,7]},'knife':{'duration':18,'windup':[0,3],'sweep':[4,10],'followthrough':[11,17]},'units':'native gameplay updates; original walk pixels and metadata retained'},indent=2)+'\n')
print('Authored four operative combat poses and six directional weapon effects; walking frames preserved.')
