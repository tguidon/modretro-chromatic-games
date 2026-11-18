"""Focused putting acceptance, using only controller inputs on the built ROM."""
import hashlib,json,math
from playtest import Game,plan,course,OUT,ROM

def green(label):
    g=Game(label);g.start()
    for _ in range(2):
        c,p,a=plan(g.state(),course[0]);g.aim(c,a);g.swing(p)
    g.until(lambda:not g.byte('view_busy'));g.tick(12)
    assert g.byte('club')==4 and g.byte('view_zoom')==2 and g.byte('view_active')==1
    return g

g=green('putt-controls');g.snap('putting-read')
heading=lambda:g.byte('angle')*4+g.byte('fine')
h=heading();g.press('right');assert heading()==(h+1)%256
g.press('left');assert heading()==h
p=g.byte('power');g.press('up');assert g.byte('power')==p+1
g.press('down');assert g.byte('power')==p
old=g.byte('putt_long');g.press('select');assert g.byte('putt_long')!=old
g.snap('putting-long-range');g.press('select');assert g.byte('putt_long')==old
before=g.state();g.press('a');g.tick(24);g.snap('putting-meter');g.press('b')
assert g.byte('mode')==0 and g.byte('view_active')==1
assert all(g.state()[k]==before[k] for k in ('x','y','strokes','total','power'))
# Actual OAM must contain visible objects over the window: ball/cup/aim guides.
oam=g.p.memory[0xfe00:0xfea0]
visible=sum(0<oam[i]<144 and 0<oam[i+1]<168 for i in range(0,160,4))
assert visible>=4,visible
g.close()
results={}
for name,angle,power in [('uphill',48,50),('downhill',16,50),('cross-slope',56,85),('firm-through-cup',40,100)]:
    g=green('putt-'+name);start=g.state();g.aim(4,angle);r=g.swing(power)
    path=r['positions'];distance=math.hypot(r['result']['x']-start['x'],r['result']['y']-start['y'])
    x0,y0,_=path[0];x1,y1,_=path[-1];dx=x1-x0;dy=y1-y0
    curve=max(abs(dx*(y-y0)-dy*(x-x0))/max(1,math.hypot(dx,dy))/16 for x,y,z in path)
    assert r['maxHeight']==0
    results[name]={'distancePixels':distance,'curvePixels':curve,'frames':len(path),'strokes':r['result']['strokes'],'mode':r['result']['mode']}
    if name=='firm-through-cup':assert r['result']['mode']==0,'Fast putt should run past the cup'
    g.snap('putting-'+name);g.close()
assert results['downhill']['distancePixels']>results['uphill']['distancePixels']+1,results
assert results['cross-slope']['curvePixels']>.4,results
report={'result':'pass','romSha256':hashlib.sha256(ROM.read_bytes()).hexdigest(),'visibleObjects':visible,'checks':['2x green view','256-direction fine aiming','1 percent power adjustment','short/long range toggle','cancel preserves stroke and position','visible ball/cup/guide sprites over viewport','downhill rolls farther','cross-slope break','firm putt runs past cup','putts stay on ground'],'shots':results}
(OUT/'putting-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
