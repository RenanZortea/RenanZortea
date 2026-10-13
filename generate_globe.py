"""Render a looping ASCII Earth. Requires Python 3 and Pillow; no network requests."""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'assets'
OUT.mkdir(exist_ok=True)
FONT = ImageFont.truetype('/usr/share/fonts/TTF/FiraCodeNerdFont-Retina.ttf', 14)
# Hand-drawn, deliberately low-resolution continent silhouettes (longitude, latitude).
LAND = [
 [(-168,70),(-140,72),(-125,60),(-110,57),(-95,72),(-60,53),(-80,26),(-98,17),(-112,30),(-128,50),(-160,60)],
 [(-98,22),(-84,22),(-77,8),(-83,8)],
 [(-81,12),(-66,10),(-50,0),(-35,-8),(-43,-23),(-55,-35),(-68,-55),(-75,-40),(-80,-10)],
 [(-52,60),(-42,60),(-20,80),(-48,84),(-65,75)],
 [(-17,36),(10,37),(33,30),(43,12),(51,11),(40,-12),(32,-30),(18,-35),(8,-20),(-5,5),(-17,15)],
 [(-10,36),(-10,44),(5,50),(10,59),(28,71),(48,68),(60,55),(40,40),(28,36),(15,42)],
 [(30,40),(45,65),(100,78),(150,70),(179,65),(165,52),(140,45),(125,25),(110,20),(105,0),(95,5),(80,28),(73,8),(60,25),(45,12),(35,30)],
 [(112,-11),(135,-12),(145,-20),(154,-28),(146,-39),(130,-33),(114,-35)],
 [(47,-13),(51,-16),(48,-26),(44,-23)],
 [(130,32),(142,45),(145,40),(137,32)],
 [(96,5),(108,-5),(120,-8),(130,-5),(141,-8),(133,-11),(113,-9),(102,-5)],
 [(166,-35),(178,-38),(170,-47),(166,-45)],
 [(-180,-74),(-120,-70),(-60,-75),(0,-71),(60,-73),(120,-70),(180,-74),(180,-90),(-180,-90)],
]
def inside(x,y,p):
    result=False
    j=len(p)-1
    for i,(xi,yi) in enumerate(p):
        xj,yj=p[j]
        if (yi>y)!=(yj>y) and x < (xj-xi)*(y-yi)/(yj-yi)+xi:
            result=not result
        j=i
    return result

# Precompute the map and visible sphere geometry for fast, deterministic frames.
mask=Image.new('1',(720,360))
md=ImageDraw.Draw(mask)
for polygon in LAND:
    md.polygon([((lon+180)*2,(90-lat)*2) for lon,lat in polygon],fill=1)
points=[]
for row in range(31):
    y=(row-15)/15.5
    for col in range(63):
        x=(col-31)/31.5
        if x*x+y*y>=1: continue
        z=math.sqrt(1-x*x-y*y)
        lat=math.asin(-y)
        lon=math.atan2(x,z)
        light=max(.15, -.35*x-.25*y+.85*z)
        points.append((col,row,lat,lon,light))
frames=[]
for frame in range(96):
    im=Image.new('RGB',(720,600),'#0d1117')
    draw=ImageDraw.Draw(im)
    draw.text((34,22),'RENAN / WORLD WIDE BUILDER',font=FONT,fill='#8b949e')
    draw.line((34,50,686,50),fill='#263342')
    phase=2*math.pi*frame/96
    for col,row,lat,lon,light in points:
        longitude=(math.degrees(lon+phase)+180)%360-180
        land=mask.getpixel((int((longitude+180)*2)%720,min(359,int(180-math.degrees(lat)*2))))
        if land:
            char=':+*#%@'[min(5,int(light*6))]
            color=(int(60+80*light),int(115+125*light),int(100+110*light))
        else:
            char='.' if light<.65 else ':'
            color=(int(25+22*light),int(45+38*light),int(60+48*light))
        draw.text((81+col*9,72+row*15),char,font=FONT,fill=color)
    draw.line((34,553,686,553),fill='#263342')
    draw.text((34,568),'ASCII EARTH',font=FONT,fill='#6fe3ba')
    draw.text((466,568),'KEEP EXPLORING.',font=FONT,fill='#8b949e')
    frames.append(im)
# A single shared palette avoids flicker during rotation.
palette=frames[0].quantize(colors=64)
encoded=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
encoded[0].save(OUT/'ascii-globe.gif',save_all=True,append_images=encoded[1:],duration=80,loop=0,optimize=False,disposal=1)
frames[0].save(OUT/'ascii-globe-preview.png')
print(f'Generated {len(frames)} frames: {(OUT / "ascii-globe.gif").stat().st_size:,} bytes')
