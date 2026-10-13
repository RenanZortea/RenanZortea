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
# Precompute the map and visible sphere geometry for fast, deterministic frames.
mask=Image.new('1',(720,360))
md=ImageDraw.Draw(mask)
for polygon in LAND:
    md.polygon([((lon+180)*2,(90-lat)*2) for lon,lat in polygon],fill=1)
points=[]
for row in range(39):
    y=(row-19)*15/283.5
    for col in range(63):
        x=(col-31)/31.5
        if x*x+y*y>=1: continue
        z=math.sqrt(1-x*x-y*y)
        lat=math.asin(-y)
        lon=math.atan2(x,z)
        light=max(.15, -.35*x-.25*y+.85*z)
        points.append((col,row,lat,lon,light))
# Indexed drawing keeps all empty pixels truly transparent (including between glyphs).
# Separate monochrome palettes keep the artwork readable in both GitHub themes.
palette_dark = [0,0,0, 245,245,245, 115,115,115, 165,165,165] + [0,0,0]*252
palette_light = [255,255,255, 25,25,25, 155,155,155, 95,95,95] + [0,0,0]*252

def distant_bodies(draw):
    # Small static ASCII sun, with eight detached rays.
    cx, cy = 837, 100
    for row in range(-3,4):
        for col in range(-5,6):
            r=(col*9)**2+(row*15)**2
            if r < 39**2:
                draw.text((cx+col*9,cy+row*15),'*' if r>25**2 else '@',font=FONT,fill=3,anchor='mm')
    for dx,dy,char in [(0,-61,'|'),(0,61,'|'),(-63,0,'-'),(63,0,'-'),(-48,-48,'\\'),(48,48,'\\'),(48,-48,'/'),(-48,48,'/')]:
        draw.text((cx+dx,cy+dy),char,font=FONT,fill=3,anchor='mm')
    # Crescent formed by subtracting an offset circle from a disk.
    cx, cy = 118, 655
    for row in range(-3,4):
        for col in range(-5,6):
            x,y=col*9,row*15
            if x*x+y*y < 43**2 and (x-22)**2+(y+9)**2 > 39**2:
                draw.text((cx+x,cy+y),'+' if x<-27 else '*',font=FONT,fill=3,anchor='mm')

frames=[]
for frame in range(96):
    im=Image.new('P',(960,760),0)
    im.putpalette(palette_dark)
    draw=ImageDraw.Draw(im)
    distant_bodies(draw)
    phase=2*math.pi*frame/96
    for col,row,lat,lon,light in points:
        longitude=(math.degrees(lon+phase)+180)%360-180
        land=mask.getpixel((int((longitude+180)*2)%720,min(359,int(180-math.degrees(lat)*2))))
        char=':+*#%@'[min(5,int(light*6))] if land else ('.' if light<.65 else ':')
        draw.text((480+(col-31)*9,380+(row-19)*15),char,font=FONT,fill=1 if land else 2,anchor='mm')
    frames.append(im)

for name,palette in [('ascii-globe.gif',palette_dark),('ascii-globe-light.gif',palette_light)]:
    for im in frames:
        im.putpalette(palette)
    # Clear each previous frame to transparent, avoiding trails from moving continents.
    frames[0].save(OUT/name,save_all=True,append_images=frames[1:],duration=80,
                   loop=0,optimize=False,disposal=2,transparency=0)
    print(f'Generated {name}: {(OUT/name).stat().st_size:,} bytes')
frames[0].putpalette(palette_dark)
frames[0].info['transparency']=0
frames[0].convert('RGBA').save(OUT/'ascii-globe-preview.png')
