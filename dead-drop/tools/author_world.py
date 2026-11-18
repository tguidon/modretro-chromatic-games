"""Build the original native world from reviewed room recipes and stable IDs.
New resources are deterministic; imported asset IDs and unknown metadata survive.
"""
from pathlib import Path
import json,uuid,textwrap
ROOT=Path(__file__).resolve().parents[1]
def load(p):return json.loads(p.read_text())
def save(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,indent=2)+'\n')
def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'dead-drop/'+s))
def asset(n,k='sprites'):return load(ROOT/f'assets/{k}/{n}.png.gbsres')['id']
serial=0
def ev(cmd,args=None,children=None):
 global serial
 serial+=1;o={'id':uid('event/'+str(serial)),'command':cmd,'args':args or {}}
 if children:o['children']=children
 return o
def text(s):
 pages=[]
 for para in s.split('|'):
  lines=textwrap.wrap(para,19,break_long_words=False,break_on_hyphens=False)
  pages.extend('\n'.join(lines[i:i+3]) for i in range(0,len(lines),3))
 return ev('EVENT_TEXT',{'text':pages})
def setv(n,val=1):return ev('EVENT_SET_VALUE',{'variable':str(n),'value':{'type':'number','value':val}})
def iff(n,yes,no=None,value=1,op='=='):return ev('EVENT_IF',{'condition':{'type':'eq' if op=='==' else 'ne','valueA':{'type':'variable','value':str(n)},'valueB':{'type':'number','value':value}}},{'true':yes,'false':no or []})
def cmd(op,value=0):return ev('EVENT_DEAD_DROP',{'op':op,'value':value})
def trans(n,x=6,y=29,d='up'):
 return ev('EVENT_SWITCH_SCENE',{'sceneId':uid(f'room/{n}'),'x':{'type':'number','value':x},'y':{'type':'number','value':y},'direction':d,'fadeSpeed':'2'})
rooms=load(ROOT/'design/rooms.json')
pals=[uid(f'palette/{i}') for i in range(7)]+['default-ui']
base=load(ROOT/'project/scenes/start/scene.gbsres')
# Original sprite palettes. The common three visible shades stay readable.
for name,colors in [('spy',['DBE8D8','9BE8C0','447E89','102330']),('guard',['EDD9A2','C8A577','906D57','1A2733']),('cone',['E8C887','CFA45B','7D7B58','263F49'])]:
 save(ROOT/f'project/palettes/{name}.gbsres',{'_resourceType':'palette','id':uid('pal/'+name),'name':name.title(),'colors':colors})
# Assign the imported sprite tiles to their hardware palette slots.
for sprite_name,slot in [('sentry',1),('sight',2)]:
 p=ROOT/f'assets/sprites/{sprite_name}.png.gbsres';data=load(p)
 for state in data['states']:
  for animation in state['animations']:
   for frame in animation['frames']:
    for tile in frame['tiles']:tile['paletteIndex']=slot
 save(p,data)
# Sprite metadata palette indices are assigned per metasprite tile by compiler
# from each actor's paletteId; sight markers and operative have distinct families.
brief={
0:'CONTROL / 03:17. The tanker MERIDIAN carries stolen guidance chips. Get aboard. Leave no signal.|A: knife. Hold A to use a terminal. B: pistol. SELECT: crouch. START: pause.|Dark bays conceal you. Dotted marks show guard facing. Cover blocks sight and bullets. Hold A near terminals for 3 seconds. Stay out of sight.',
1:'AFT DECK. Patrols reverse at cover. Watch, then cross behind them. Yellow stripes mark the long route.',
2:'CONTAINER SPINE. Grated slots under bulkheads are crawl spaces. Crouch to use them.',
6:'SECURITY. Get the access card from the mint terminal near the north hatch.',
9:'PUMP CONTROL. Charges need the manifest arming codes. Scout this room, then continue to the BRIDGE.',
10:'ENGINE ROOM. Remember this regulator. Return after copying the BRIDGE manifest. Keep going north.',
11:'GENERATOR. Kill the cargo floodlights. Your shadow route will become safer.',
14:'ARCHIVE. The manifest is on the bridge. This terminal has the cipher route.',
17:'BRIDGE. Copy the manifest and arming codes. Then return south to PUMP CONTROL and ENGINE ROOM.',
19:'MISSILE CARGO. Place your final charge. We only burn the guidance hardware.',
20:'LAUNCH CONTROL. Wipe the targeting uplink, then move to the bow lifeboat.',
21:'EXFIL. The ship is waking up. Keep moving. Two sectors to the boat.'}
objectives={
6:(1,'ACCESS CARD COPIED. The service trunk is open. An armory door is in the east wall.','The card opens SERVICE TRUNK.'),
9:(3,'CHARGE 1 / COOLANT. Armed remotely. Next: ENGINE ROOM, one sector north.','Coolant charge is ready.'),
10:(4,'CHARGE 2 / REGULATOR. Next: CIPHER VAULT, north of the bridge.','Regulator charge is ready.'),
11:(2,'CARGO LIGHTS OFF. Deep shadow now hides you better throughout the tanker.','Cargo blackout is active.'),
17:(0,'MANIFEST COPIED. Arming codes acquired. Return SOUTH: PUMP CONTROL, then ENGINE ROOM.|Security teams are moving into engineering. New patrols are on your return route.','Arm both engineering charges, then return north to the CIPHER VAULT.'),
18:(10,'CIPHER CRACKED. Missile cargo unlocked. One charge remains.','Cipher copied. Cargo is open.'),
19:(5,'CHARGE 3 / GUIDANCE. All devices are in place. Reach LAUNCH CONTROL.','Guidance charge is ready.'),
20:(6,'UPLINK ERASED. Charges will fire after extraction. Reach the bow lifeboat.','Uplink erased. Get to the boat.')}
intel={14:(7,'INTEL / GHOST LEDGER. A private fleet moved the hardware. A name: ORCHID.'),15:(8,'INTEL / RADIO LOG. A friendly deckhand left supplies in the infirmary.'),26:(9,'INTEL / FALSE FLAG. The tanker crew are prisoners. Your report will clear them.')}
gates={6:(1,'Copy the access card at the north terminal.'),11:(2,'Shut off the cargo lights at the terminal.'),17:(0,'Copy the manifest before leaving the bridge.'),18:(10,'Crack the cipher at the terminal.'),19:(5,'Plant the final charge before leaving.'),20:(6,'Erase the targeting uplink first.')}
side={5:24,6:25,16:26,4:27}
sideback={v:k for k,v in side.items()}
hints=['The hatch north leads deeper into the tanker. Follow mint arrows.','A suppressed shot still carries a short distance. Save rounds for blocked routes.','A knife is silent. Approach behind a sentry and press A at close range.','Each sector entrance is a session checkpoint. On defeat, you return there.','The dark floor bays hide your silhouette. Crouching helps in light too.','The east hatch leads to the infirmary. Supplies are limited.','Copy the card. The east hatch leads to the armory.','Watch the facing dots. Move when the patrol turns away.','Coolant controls lie north. Look for the terminal above the second bulkhead.']
for n,r in enumerate(rooms):
 folder=ROOT/f'project/scenes/sector_{n:02d}'
 bgpath=ROOT/f'assets/backgrounds/sector_{n:02d}.png.gbsres';bg=load(bgpath);bg.update({'tileColors':r['tileColors'],'name':r['name']});save(bgpath,bg)
 s=base.copy();s.update({'id':r['id'],'_index':n+1,'type':'STEALTH','name':f'{n+1:02d} {r["name"].title()}','symbol':f'scene_sector_{n:02d}','x':(n%6)*360,'y':220+(n//6)*330,'width':40,'height':36,'backgroundId':bg['id'],'paletteIds':pals,'spritePaletteIds':[uid('pal/spy'),uid('pal/guard'),uid('pal/cone')]+[uid('pal/spy')]*5,'playerSpriteSheetId':asset('operative'),'collisions':r['collisions'],'autoFadeSpeed':1})
 script=[ev('EVENT_REMOVE_INPUT_SCRIPT',{'input':['start']}),cmd(1,n)]
 if n in brief:script.append(iff(100+n,[],[setv(100+n),cmd(4),text(brief[n])]))
 s['script']=script;save(folder/'scene.gbsres',s)
 def actor(idx,name,x,y,sprite,direction='down',script=None,palette='spy'):
  o={'_resourceType':'actor','id':uid(f'actor/{n}/{idx}'),'_index':idx-1,'name':name,'symbol':f'actor_s{n}_{idx}','x':x,'y':y,'frame':0,'animate':True,'spriteSheetId':asset(sprite),'paletteId':uid('pal/'+palette),'direction':direction,'moveSpeed':1,'animSpeed':15,'isPinned':False,'persistent':True,'collisionGroup':'1' if idx<=4 else '','collisionEnabled':False,'script':script or [],'startScript':[],'updateScript':[],'hit1Script':[],'hit2Script':[],'hit3Script':[]}
  save(folder/f'actors/{idx:02d}.gbsres',o)
 positions=[(6,25,'up'),(33,16,'up'),(8,6,'right'),(26,6,'left')]
 # Alternate routes force a different approach in later compartments.
 if n%3==1:positions=[(12,29,'right'),(21,20,'left'),(33,6,'down'),(10,5,'right')]
 if n%3==2:positions=[(29,27,'up'),(7,16,'down'),(16,8,'right'),(33,5,'left')]
 for i,(x,y,d) in enumerate(positions):actor(i+1,f'Sentry {i+1}',x,y,'sentry',d,palette='guard')
 for i,(x,y,d) in enumerate(positions):actor(i+5,f'Sight marker {i+1}',x,y,'sight',d,palette='cone')
 use=[cmd(4)]
 if n in objectives:
  v,first,again=objectives[n];firstpath=[setv(v),text(first)]
  if n==11:firstpath.insert(0,cmd(3))
  if n==6:firstpath.insert(0,cmd(6,1))
  if n==17:firstpath.insert(0,cmd(5));firstpath.insert(0,cmd(6,2))
  if n==10:firstpath.insert(0,cmd(6,3))
  if n==19:firstpath.insert(0,cmd(6,4))
  if n==20:firstpath.insert(0,cmd(6,5))
  if n in [9,10]:firstpath=[iff(0,firstpath,[text('Arming codes required. Copy the manifest on the BRIDGE, then return here.')])]
  if n==20:
   firstpath=[iff(0,[iff(3,[iff(4,[iff(5,firstpath,[text('Guidance charge missing. Return to missile cargo.')])],[text('Regulator charge missing. Return to engine room.')])],[text('Coolant charge missing. Return to pump control.')])],[text('Manifest missing. Return to the bridge.')])]
  use.append(iff(v,[text(again)],firstpath))
 elif n in intel:
  v,t=intel[n];use.append(iff(v,[text('Intel already copied.')],[setv(v),text(t)]))
 elif n in [0,5,12,21,24,25]:
  qty=12 if n==25 else 6
  use.append(iff(200+n,[text('Supply cache empty. Keep moving.')],[setv(200+n),cmd(2,qty),text(f'FIELD CACHE. Health restored. {qty} suppressed rounds recovered.')]))
 elif n==23:
  ending=[cmd(4),text('CONTROL: Clear of the ship. Triggering the devices.|Guidance hardware destroyed. The tanker and crew survive. The manifest is already on the wire.'),iff(7,[iff(8,[iff(9,[text('ALL INTEL RECOVERED. ORCHID network exposed. A flawless investigation.')],[text('Two intel files found. ORCHID remains at large.')])],[text('Archive intel secured.')])],[text('Mission complete. Optional intel remains aboard.')]),text('DEAD DROP COMPLETE. Thank you for playing.|Press A to return to the title.'),ev('EVENT_SWITCH_SCENE',{'sceneId':base['id'],'x':{'type':'number','value':9},'y':{'type':'number','value':9},'fadeSpeed':'2'})]
  use.append(iff(6,ending,[text('Extraction denied. Erase the uplink in LAUNCH CONTROL first.')]))
 else:use.append(text(hints[n%len(hints)]))
 actor(9,'Mission terminal',9 if n==0 else 29,29 if n==0 else 6,'terminal',script=use)
 actor(10,'Suppressed tracer',6,29,'tracer')
 def trigger(name,x,y,w,h,script):
  o={'_resourceType':'trigger','id':uid(f'trigger/{n}/{name}'),'_index':0 if name=='north' else 1 if name=='south' else 2,'name':name,'symbol':f'trigger_s{n}_{name}','x':x,'y':y,'width':w,'height':h,'script':script,'leaveScript':[]};save(folder/f'triggers/{name}.gbsres',o)
 if n<23:
  path=[trans(n+1)]
  if n==18:path=[iff(3,[iff(4,path,[cmd(4),text('ENGINE charge missing. Return south to ENGINE ROOM.'),ev('EVENT_ACTOR_SET_POSITION',{'actorId':'player','x':{'type':'number','value':31},'y':{'type':'number','value':5}})])],[cmd(4),text('COOLANT charge missing. Return south to PUMP CONTROL.'),ev('EVENT_ACTOR_SET_POSITION',{'actorId':'player','x':{'type':'number','value':31},'y':{'type':'number','value':5}})])]
  if n in gates:
   v,t=gates[n];path=[iff(v,path,[cmd(4),text(t),ev('EVENT_ACTOR_SET_POSITION',{'actorId':'player','x':{'type':'number','value':31},'y':{'type':'number','value':5}})])]
  trigger('north',29,2,6,2,path)
 if 0<n<24:trigger('south',4,32,6,2,[trans(n-1,31,5,'down')])
 if n in side:
  trigger('side',35,27,2,4,[trans(side[n])])
 if n in sideback:
  trigger('south',4,32,6,2,[trans(sideback[n],34,28,'left')])
  if n==27:trigger('north',29,2,6,2,[iff(1,[trans(8)],[cmd(4),text('Service grille locked. Get the SECURITY card first. Return through the south hatch.'),ev('EVENT_ACTOR_SET_POSITION',{'actorId':'player','x':{'type':'number','value':31},'y':{'type':'number','value':5}})])])
# Retain original scene ID as the title scene; imported workshop remains preserved.
title=base.copy();title.update({'name':'Dead Drop / Title','type':'LOGO','backgroundId':asset('title','backgrounds'),'paletteIds':pals,'collisions':'','script':[ev('EVENT_ACTOR_HIDE',{'actorId':'player'}),ev('EVENT_SET_INPUT_SCRIPT',{'input':['start'],'override':True},{'true':[cmd(0)]+[setv(i,0) for i in list(range(11))+list(range(100,128))+list(range(200,228))]+[trans(0)]})],'x':0,'y':0})
save(ROOT/'project/scenes/start/scene.gbsres',title)
settings=load(ROOT/'project/settings.gbsres');settings.update({'defaultSceneTypeId':'STEALTH','defaultPlayerSprites':{**settings['defaultPlayerSprites'],'STEALTH':asset('operative')},'startSceneId':base['id'],'startX':9,'startY':9,'playerPaletteId':uid('pal/spy'),'defaultBackgroundPaletteIds':pals,'defaultSpritePaletteIds':[uid('pal/spy'),uid('pal/guard'),uid('pal/cone')]+[uid('pal/spy')]*5,'romFilename':'dead-drop'})
save(ROOT/'project/settings.gbsres',settings)
vars=load(ROOT/'project/variables.gbsres');vars['variables']=[{'id':str(i),'name':name,'symbol':'var_'+name.lower().replace(' ','_')} for i,name in enumerate(['Manifest','Access card','Blackout','Coolant charge','Regulator charge','Guidance charge','Uplink erased','Archive intel','Radio intel','Chart intel','Cipher'])]+[{'id':str(100+n),'name':f'Visited sector {n+1}','symbol':f'var_visit_{n}'} for n in range(28)]+[{'id':str(200+n),'name':f'Supply sector {n+1}','symbol':f'var_supply_{n}'} for n in range(28)];save(ROOT/'project/variables.gbsres',vars)
print(f'Authored 29 scenes, 280 actors, native transitions and {serial} events.')
