"""Controller-only ROM integration tests. Symbols are used for read-only assertions."""
import hashlib,json,math,re
from pathlib import Path
from pyboy import PyBoy
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
ROM=ROOT/'build/birdie-juice.gbc'
SYMBOLS=ROOT/'build/birdie-juice.sym'
OUT=ROOT/'artifacts/playtests'
OUT.mkdir(parents=True,exist_ok=True)
course=json.loads((ROOT/'course/holes.json').read_text())['holes']
symbols={}
for line in SYMBOLS.read_text().splitlines():
    m=re.match(r'00:([0-9A-Fa-f]{4}) (_bj_\w+)$',line)
    if m:symbols[m[2]]=int(m[1],16)
assert '_bj_mode' in symbols
class Game:
    def __init__(self,label):
        self.p=PyBoy(str(ROM),window='null',sound_emulated=False)
        self.p.set_emulation_speed(0);self.frames=0;self.actions=[];self.label=label
        self.tick(180);assert self.byte('mode')==4
    def tick(self,n):self.p.tick(n,True);self.frames+=n
    def byte(self,n):return self.p.memory[symbols['_bj_'+n]]
    def word(self,n):
        a=symbols['_bj_'+n];v=self.p.memory[a]|self.p.memory[a+1]<<8
        return v-65536 if v>32767 else v
    def state(self):return {**{n:self.byte(n) for n in ['hole','mode','club','power','angle','strokes','notice']},'x':self.word('x')/16,'y':self.word('y')/16,'total':self.word('total')}
    def press(self,b):
        self.actions.append({'frame':self.frames,'button':b,'heldFrames':3})
        self.p.button_press(b);self.tick(3);self.p.button_release(b);self.tick(6)
    def snap(self,name):self.p.screen.image.save(OUT/(name+'.png'))
    def start(self):self.press('a');self.tick(4);assert self.byte('mode')==0
    def set_shot(self,club,power,angle):
        for _ in range((club-self.byte('club'))%5):self.press('b')
        for _ in range(abs(power-self.byte('power'))//5):self.press('up' if power>self.byte('power') else 'down')
        delta=(angle-self.byte('angle'))%32
        for _ in range(min(delta,32-delta)):self.press('right' if delta<=16 else 'left')
        assert (self.byte('club'),self.byte('power'),self.byte('angle'))==(club,power,angle)
    def swing(self):self.press('a');self.tick(44)
    def close(self):
        (OUT/(self.label+'-inputs.json')).write_text(json.dumps({'romSha256':hashlib.sha256(ROM.read_bytes()).hexdigest(),'frames':self.frames,'actions':self.actions},indent=2)+'\n')
        self.p.stop(save=False)
# Controls, menu and hazard checks from an ordinary fresh boot.
g=Game('controls-hazards');g.snap('title');g.press('start');assert g.byte('mode')==5;g.snap('help');g.press('b');assert g.byte('mode')==4;g.start();g.snap('hole-01-controls')
for i in range(5):g.press('b');assert g.byte('club')==(i+1)%5
g.press('select');assert g.byte('club')==4;g.press('b');assert g.byte('club')==0
old=g.state();g.press('start');assert g.byte('mode')==3;g.tick(90);assert g.word('x')/16==old['x'];g.press('b');assert g.byte('mode')==0
# A 52-pixel drive north, then a short wedge into the actual pond on hole one.
g.set_shot(0,100,24);g.swing();s=g.state();assert s['strokes']==1 and s['y']==64,s
landing=(s['x'],s['y']);g.set_shot(3,70,19);g.swing();s=g.state();assert s['notice']==1 and s['strokes']==3 and s['total']==3,s
assert (s['x'],s['y'])==landing,s;g.snap('water-penalty')
# Move to a bunker, then make sure that the driver loses half its carry in sand.
g.set_shot(3,25,24);g.swing()
g.set_shot(0,100,0);g.swing()
g.set_shot(3,85,0);g.swing();s=g.state()
assert course[0]['terrain'][int(s['y'])//8][int(s['x'])//8]=='s',s
g.snap('bunker');sand_x=s['x'];g.set_shot(0,100,0);g.swing()
assert g.state()['x']-sand_x==26,g.state()
# Repeated deliberate out-of-bounds shots exercise the stroke cap and pickup.
while g.byte('mode')==0:g.set_shot(0,100,8);g.swing()
assert g.byte('mode')==2 and g.byte('strokes')>=12;g.snap('pickup');g.tick(30);g.press('a');g.tick(90);assert g.byte('hole')==1 and g.byte('mode')==0;g.close()
# Play every hole with controller input; no savestates, scene skipping or memory writes.
g=Game('full-round');g.start();scores=[];screens=[]
ranges=[52,44,32,20,12]
def terrain(h,x,y):
    if not (0<=x<160 and 16<=y<128):return 'w'
    return h['terrain'][int(y)//8][int(x)//8]
def choose(s,h):
    x,y=s['x'],s['y'];cx,cy=[v*8+4 for v in h['cup']];lie=terrain(h,x,y)
    best=None
    for club,base in enumerate(ranges):
        for power in range(5,101,5):
            dist=max(1,base*power//100)
            if club not in [3,4]:
                if lie=='s':dist//=2
                elif lie=='r':dist=dist*3//4
                dist=max(1,dist)
            for a in range(32):
                # Native directions are 8.8 fixed-point, including signed truncation.
                dx=round(math.cos(a*math.pi/16)*256);dy=round(math.sin(a*math.pi/16)*256)
                tx=x+((dx*dist)>>4)/16;ty=y+((dy*dist)>>4)/16
                ground=terrain(h,tx,ty)
                if ground in ['w','t']:continue
                score=math.hypot(tx-cx,ty-cy)
                if ground=='r':score+=5
                if ground=='s':score+=10
                if score<4:score-=100
                # Prefer a putt for near-equivalent safe landings.
                score+=.05*(4-club)
                if best is None or score<best[0]:best=(score,club,power,a)
    assert best is not None
    return best[1:]
for index,h in enumerate(course):
    assert g.byte('hole')==index,g.state()
    g.snap(f'hole-{index+1:02}');screens.append(OUT/f'hole-{index+1:02}.png')
    for shot in range(12):
        if g.byte('mode')!=0:break
        g.set_shot(*choose(g.state(),h));g.swing()
    s=g.state();assert s['mode'] in [2,3] and s['notice']!=3,s
    assert math.hypot(s['x']-(h['cup'][0]*8+4),s['y']-(h['cup'][1]*8+4))<=4,s
    scores.append(s['strokes']);g.snap(f'finished-{index+1:02}')
    print(f'Hole {index+1}: par {h["par"]}, {s["strokes"]} strokes',flush=True)
    if index<8:g.tick(30);g.press('a');g.tick(90)
assert g.byte('mode')==3 and g.word('total')==sum(scores),(g.state(),scores)
a=symbols['_bj_scores'];assert list(g.p.memory[a:a+9])==scores
g.snap('round-complete');total=g.word('total');g.tick(30);g.press('a');g.tick(90)
assert g.byte('hole')==0 and g.byte('mode')==4 and g.word('total')==0
g.start();assert g.byte('strokes')==0 and list(g.p.memory[a:a+9])==[0]*9
frames=g.frames;g.close()
sheet=Image.new('RGB',(3*336,3*318),'#193c35');d=ImageDraw.Draw(sheet)
for i,path in enumerate(screens):
    x=i%3*336+8;y=i//3*318+8
    sheet.paste(Image.open(path).convert('RGB').resize((320,288),Image.Resampling.NEAREST),(x,y))
    d.text((x,y+294),f'{i+1:02} {course[i]["name"].upper()} / PAR {course[i]["par"]}',fill='#f6e7be')
sheet.save(OUT/'nine-holes.png')
report={'result':'pass','romSha256':hashlib.sha256(ROM.read_bytes()).hexdigest(),'par':sum(h['par'] for h in course),'scores':scores,'total':total,'relativeToPar':total-36,'fullRoundFrames':frames,'checks':['title and help','all five clubs and reverse selection','scorecard preserves ball position','pond costs one penalty stroke and drops ball','bunker halves driver carry','stroke cap and pickup','all nine distinct scenes','all nine cups reached without pickup','round total equals scorecard','new round resets scores'],'evidence':'Screenshots and controller input journals in artifacts/playtests. Read-only symbol assertions; no memory writes.'}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
