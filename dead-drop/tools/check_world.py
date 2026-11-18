"""Connectivity and native-resource checks; these do not substitute for ROM play."""
from pathlib import Path
import json,collections,re
R=Path(__file__).resolve().parents[1]
def decode(s):
 out=[]
 for a,b in re.findall(r'([0-9a-f]{2})([0-9a-f]+)\+',s):out.extend([int(a,16)]*int(b,16))
 return out
def path(cols,start,end,crawl=False):
 def free(p):
  x,y=p
  for xx,yy in [(x+3,y+1),(x+12,y+1),(x+3,y+7),(x+12,y+7)]:
   if xx<0 or yy<0 or xx>=320 or yy>=288:return False
   c=cols[(yy//8)*40+xx//8]
   if c&15 or (c&32 and not crawl):return False
  return True
 todo=collections.deque([start]);prev={start:None}
 while todo:
  p=todo.popleft()
  if p==end:
   steps=[]
   while prev[p] is not None:steps.append(p);p=prev[p]
   steps.reverse();ways=[];old=start;lastdir=None
   for p in steps:
    d=(p[0]-old[0],p[1]-old[1])
    if lastdir is not None and d!=lastdir:ways.append(old)
    lastdir=d;old=p
   ways.append(end);return ways,len(steps)*4
  for dx,dy in [(0,-4),(4,0),(0,4),(-4,0)]:
   q=(p[0]+dx,p[1]+dy)
   if q not in prev and free(q):prev[q]=p;todo.append(q)
 raise AssertionError(f'No path {start}->{end}')
plans=[]
for n in range(28):
 s=json.loads((R/f'project/scenes/sector_{n:02d}/scene.gbsres').read_text());cols=decode(s['collisions']);assert len(cols)==1440
 target=(72,232) if n==0 else (232,56)
 route,dist=path(cols,(48,232),target)
 out,d2=path(cols,target,(248,24))
 if n in [4,5,6,16]:path(cols,(48,232),(276,232))
 plans.append({'sector':n,'terminal':route,'exit':out,'distance':dist+d2})
 assert len(list((R/f'project/scenes/sector_{n:02d}/actors').glob('*.gbsres')))==10
 for actor_index in range(1,5):
  a=json.loads((R/f'project/scenes/sector_{n:02d}/actors/{actor_index:02d}.gbsres').read_text())
  for dx,dy in [(3,1),(12,1),(3,7),(12,7)]:
   c=cols[((a['y']*8+dy)//8)*40+(a['x']*8+dx)//8]
   assert not c&47, f'Sector {n+1} guard {actor_index} starts in solid cover or a vent'

(R/'design/navigation.json').write_text(json.dumps(plans,indent=2)+'\n')
print('PASS: 28 entrance-to-objective-to-exit routes; 4 side doors; 112 valid guard spawns; 280 actor slots.')
print('Standing route pixel distance:',sum(x['distance'] for x in plans[:24]))
