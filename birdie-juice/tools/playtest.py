"""Controller-only regression play on the exact ROM; symbols are read-only.

Uses timing feedback from the meter, not memory writes or teleports. Shot planning
is deliberately approximate, so this checks the playable loop rather than proving
that a duplicate physics implementation agrees with itself.
"""
import argparse,hashlib,json,math,re
from pathlib import Path
from pyboy import PyBoy
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--rom',type=Path,help='Exact ROM to test; requires matching --symbols')
parser.add_argument('--symbols',type=Path,help='Matching .sym or .noi file')
parser.add_argument('--output',type=Path,default=ROOT/'artifacts/playtests/regression')
args=parser.parse_args()
if args.rom and not args.symbols:parser.error('--rom requires matching --symbols')
ROM=args.rom.resolve() if args.rom else ROOT/'build/birdie-juice.gbc'
NOI=ROOT/'build/birdie-juice.gbc.debug/symbols.noi'
SYM=ROOT/'build/birdie-juice.sym'
OUT=args.output.resolve();OUT.mkdir(parents=True,exist_ok=True)
completed_frames=[]
course=json.loads((ROOT/'course/holes.json').read_text())['holes']
terrain_masks=[Image.open(ROOT/f'course/art/hole_{n:02}_terrain.png') for n in range(1,10)]
symbols={}
source=args.symbols or (NOI if NOI.exists() and NOI.stat().st_mtime>=ROM.stat().st_mtime-2 else SYM)
for line in source.read_text().splitlines():
    m=re.match(r'DEF (_bj_\w+) 0x([0-9A-Fa-f]+)$',line)
    if m and int(m[2],16)>=0xc000:symbols[m[1]]=int(m[2],16)
    m=re.match(r'00:([0-9A-Fa-f]{4}) (_bj_\w+)$',line)
    if m:symbols[m[2]]=int(m[1],16)
assert '_bj_meter' in symbols,'Build current ROM with debug artifacts first'
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
    def state(self):return {**{n:self.byte(n) for n in ['hole','mode','club','power','angle','strokes','notice','bounces','roll_frames']},'x':self.word('x')/16,'y':self.word('y')/16,'z':self.word('z')/16,'accuracy':self.word('accuracy'),'total':self.word('total')}
    def press(self,b):
        if '_bj_view_busy' in symbols:self.until(lambda:not self.byte('view_busy'))
        self.actions.append({'frame':self.frames,'button':b,'heldFrames':3})
        self.p.button_press(b);self.tick(3);self.p.button_release(b);self.tick(3)
        if '_bj_view_busy' in symbols:
            self.until(lambda:not self.byte('view_busy'));self.tick(3)
    def until(self,fn,limit=500):
        for _ in range(limit):
            if fn():return
            self.tick(1)
        raise AssertionError(('timeout',self.state()))
    def snap(self,name):self.p.screen.image.save(OUT/(name+'.png'))
    def start(self):self.press('a');assert self.byte('mode')==0
    def aim(self,club,angle):
        assert self.byte('mode')==0,self.state()
        for _ in range((club-self.byte('club'))%5):self.press('b')
        circle=256 if club==4 else 64
        current=self.byte('angle')*4+self.byte('fine') if club==4 else self.byte('angle')
        target=angle*4 if club==4 else angle
        delta=(target-current)%circle
        for _ in range(min(delta,circle-delta)):self.press('right' if delta<=circle//2 else 'left')
        assert (self.byte('club'),self.byte('angle'))==(club,angle),self.state()
    def swing(self,power=100,error=0,capture=False):
        self.press('a');assert self.byte('mode')==6,self.state()
        self.until(lambda:self.word('meter')>=power-2)
        if capture:self.snap('shot-power')
        self.press('a');assert self.byte('mode')==7
        self.until(lambda:self.word('meter')<=12+error)
        if capture:self.snap('shot-accuracy')
        self.press('a');assert self.byte('mode')==8
        if capture:self.snap('swing-impact')
        self.until(lambda:self.byte('mode')==1)
        max_z=0;positions=[]
        while self.byte('mode')==1:
            max_z=max(max_z,self.word('z'));positions.append((self.word('x'),self.word('y'),self.word('z')))
            if capture and len(positions) in [12,24,40,58]:self.snap('flight-'+str(len(positions)))
            self.tick(1)
            assert len(positions)<500
        self.tick(12)  # Let the settled HUD finish its VRAM writes before the next input.
        return {'maxHeight':max_z/16,'positions':positions,'result':self.state()}
    def close(self):
        (OUT/(self.label+'-inputs.json')).write_text(json.dumps({'romSha256':hashlib.sha256(ROM.read_bytes()).hexdigest(),'frames':self.frames,'actions':self.actions},indent=2)+'\n')
        self.p.stop(save=False);completed_frames.append(self.frames)

def terrain(h,x,y):
    if not (0<=x<160 and 16<=y<128):return 'w'
    return 'rfgswt'[terrain_masks[h['hole']-1].getpixel((int(x)//2*2,int(y)//2*2))]

def plan(s,h):
    x,y=s['x'],s['y'];cx,cy=[v*8+4 for v in h['cup']]
    if h['hole']==3 and x<50 and y>88:cx,cy=36,76  # Dogleg grove blocks the low driver.
    if h['hole']==6 and y>100:cx,cy=76,84  # Lay up below the island's creek.
    lie=terrain(h,x,y);distance=math.hypot(cx-x,cy-y)
    if lie=='g' and distance<23:
        # Aim a little uphill. The visible green always falls toward the lower edge.
        sx,sy=h['slope'];ux=(cx-x)/max(distance,.1);uy=(cy-y)/max(distance,.1)
        along=sx*ux+sy*uy
        cx-=(sx-along*ux)*distance*.18;cy-=(sy-along*uy)*distance*.18
        club=4;span=28 if abs(h['cup'][0]*8+4-x)+abs(h['cup'][1]*8+4-y)>12 else 12
        power=round(distance/span*100*(10-5*along)/10)
    else:
        # Approximate total carry + roll, refined by the next observed lie.
        ranges=[64,54,39,26]
        if lie in 'rs':ranges=[r*(.5 if lie=='s' else .75) for r in ranges[:3]]+[25]
        club=next((i for i in [3,2,1,0] if ranges[i]>=distance),0)
        power=round(distance/ranges[club]*100)
    angle=round(math.atan2(cy-y,cx-x)*32/math.pi)%64
    return club,max(10,min(100,power)),angle

if __name__=='__main__':
    checks=[];g=Game('controls');g.snap('title');g.press('start');assert g.byte('mode')==5;g.snap('help');g.press('b');g.start();g.snap('course-overview')
    for i in range(5):g.press('b');assert g.byte('club')==(i+1)%5
    g.press('select');assert g.byte('club')==4;g.press('b');assert g.byte('club')==0
    old=g.state();g.press('start');assert g.byte('mode')==3;g.tick(90);g.press('b');assert g.state()==old
    g.press('a');g.tick(20);g.press('b');assert g.state()==old
    checks+=['help, scorecard and club selection','cancel swing without a stroke or ball movement']
    full=g.swing(100,capture=True);assert full['maxHeight']>12,full
    assert full['result']['bounces']>=1 and full['result']['roll_frames']>0,full['result']
    assert full['result']['strokes']==1 and abs(full['result']['accuracy'])<=3,full['result']
    assert len({z for x,y,z in full['positions']})>10
    g.snap('first-drive');g.close();checks+=['gravity arc, ground impact, bounce and frictional roll','three press swing and accurate strike']
    # Paired shots from identical starts: power and timing must change the outcome.
    g=Game('half-power');g.start();half=g.swing(50);g.close()
    g=Game('mishit');g.start();miss=g.swing(100,error=36);g.close()
    start=(36,116)
    dist=lambda r:math.hypot(r['result']['x']-start[0],r['result']['y']-start[1])
    assert dist(full)>dist(half)+12,(full['result'],half['result'])
    assert math.hypot(full['result']['x']-miss['result']['x'],full['result']['y']-miss['result']['y'])>8
    checks+=['50 percent shot travels less than full power','off-center timing changes direction and distance']
    g=Game('water');g.start();g.aim(0,48);g.swing(90);s=g.state()
    assert s['notice']==1 and s['strokes']==2 and (s['x'],s['y'])==start,s
    g.snap('creek-penalty');g.close();checks+=['creek landing penalizes and drops to safe lie']
    g=Game('missed-timing');g.start();g.press('a');g.until(lambda:g.word('meter')>=78);g.press('a');g.tick(300)
    assert g.byte('mode')==0 and g.byte('strokes')>=1 and g.word('accuracy')==-20,g.state()
    g.close();checks+=['missing the accuracy window automatically produces a mishit']
    # Deliberate OB from the tee; penalty restores the original safe lie.
    g=Game('hazards');g.start();g.aim(0,32);g.swing();s=g.state();assert s['notice']==1 and s['strokes']==2 and (s['x'],s['y'])==start,s
    g.snap('penalty')
    while g.byte('mode')==0:g.aim(0,32);g.swing()
    assert g.byte('mode')==2 and g.byte('strokes')==12;g.tick(30);g.press('a');g.tick(90);assert g.byte('hole')==1;g.close()
    checks+=['out of bounds costs one penalty stroke and restores lie','12 stroke pickup and native next-hole transition']
    g=Game('full-round');g.start();scores=[];rolls=[]
    for index,h in enumerate(course):
        assert g.byte('hole')==index,g.state()
        for shot in range(12):
            if g.byte('mode')!=0:break
            s=g.state();club,power,angle=plan(s,h)
            g.aim(club,angle);r=g.swing(power)
            if club==4:rolls.append({'start':s,'path':r['positions'],'end':r['result']})
            print('Hole',index+1,'shot',shot+1,'club/power/angle',(club,power,angle),'->',g.state(),flush=True)
        s=g.state();assert s['mode'] in [2,3],s
        assert s['notice']!=3,('planner failed to finish naturally',s)
        scores.append(s['strokes']);g.snap(f'finished-{index+1:02}')
        if index<8:g.tick(30);g.press('a');g.tick(90)
    assert g.byte('mode')==3 and g.word('total')==sum(scores)
    a=symbols['_bj_scores'];assert list(g.p.memory[a:a+9])==scores
    g.snap('round-complete');frames=g.frames;g.tick(30);g.press('a');g.tick(90)
    assert g.byte('mode')==4 and g.word('total')==0
    g.start();assert list(g.p.memory[a:a+9])==[0]*9;g.close()
    bunker=Game('bunker-carry');bunker.start();bunker.swing(100)
    bunker.aim(3,6);bunker.swing(65);before=bunker.state()
    assert terrain(course[0],before['x'],before['y'])=='s',before
    bunker.snap('bunker-lie');bunker.aim(0,48);recovery=bunker.swing(100)['result']
    assert math.hypot(recovery['x']-before['x'],recovery['y']-before['y'])<dist(full)*.65,recovery
    bunker.close()
    checks+=['bunker lie reduces driver carry','all nine holes reached and holed without pickup','scorecard total and new-round reset']
    # Curvature: compare middle of an actual putt with the start/end chord.
    breaks=[]
    for r in rolls:
        path=r['path']
        if len(path)<10:continue
        x0,y0,_=path[0];x1,y1,_=path[-1];dx=x1-x0;dy=y1-y0
        if dx*dx+dy*dy==0:continue
        dev=max(abs(dx*(y-y0)-dy*(x-x0))/math.hypot(dx,dy)/16 for x,y,z in path)
        breaks.append(dev)
    assert breaks and max(breaks)>.15,breaks
    checks+=['putts curve on sloped greens in actual ROM']
    g=Game('tree-collision');g.start()
    for h in course[:2]:
        while g.byte('mode')==0:
            club,power,angle=plan(g.state(),h);g.aim(club,angle);g.swing(power)
        g.tick(30);g.press('a');g.tick(90)
    assert g.byte('hole')==2
    g.aim(0,56);r=g.swing(100);s=r['result']
    assert s['notice']==2 and s['strokes']==1,s
    assert math.hypot(s['x']-36,s['y']-116)<40,s
    g.snap('tree-deflection');g.close();checks+=['dogleg grove deflects low driver without an extra penalty']
    # Actual swing power need not be a multiple of five. D-pad changes must clamp.
    g=Game('power-upper-bound');g.start();g.swing(100);assert g.byte('power')==98
    g.press('up');assert g.byte('power')==100,g.state()
    g.press('up');assert g.byte('power')==100
    old=g.state();g.press('a');g.tick(220);assert g.byte('mode')==6
    g.snap('maximum-power-meter');g.press('b')
    assert all(g.state()[k]==v for k,v in old.items() if k!='accuracy'),g.state();g.close()
    g=Game('power-lower-bound');g.start();g.swing(10);assert g.byte('power')==8
    g.press('down');assert g.byte('power')==5,g.state()
    g.press('down');assert g.byte('power')==5
    old=g.state();g.press('a');g.tick(220);assert g.byte('mode')==6
    g.snap('minimum-power-meter');g.press('b')
    assert all(g.state()[k]==v for k,v in old.items() if k!='accuracy'),g.state();g.close()
    checks+=['target power stays within 5–100 percent after timed swings','meter cycles and cancellation work at both power limits']
    report={'result':'pass','romPath':str(ROM),'romSha256':hashlib.sha256(ROM.read_bytes()).hexdigest(),'scores':scores,'total':sum(scores),'par':36,'frames':frames,'totalTestFrames':sum(completed_frames),'driveMaxHeight':full['maxHeight'],'maxPuttCurvePixels':max(breaks),'checks':checks}
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
