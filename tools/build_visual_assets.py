"""Build shallow beveled ttk assets offline. No runtime Pillow dependency."""
import ast,base64,io
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]
P=R/'src/visual_theme.py'
s=P.read_text(encoding='utf-8');tree=ast.parse(s)
nodes={n.targets[0].id:n for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name)}
palettes=ast.literal_eval(nodes['_PALETTES'].value)
def encode(image):
 o=io.BytesIO();image.save(o,format='PNG');return base64.b64encode(o.getvalue()).decode('ascii')
def tile(fill,edge,focused=False,kind='button',pressed=False,disabled=False):
 k=4;w,h=128,64;im=Image.new('RGBA',(w*k,h*k),'#17181a' if kind in ('popup','popup_open','handover','handover_notice','tab','tab_selected','nav') else '#242528');d=ImageDraw.Draw(im)
 if kind=='nav':
  d.rectangle((0,0,w*k,h*k),fill=fill)
 elif kind=='card':
  d.rectangle((0,0,w*k,h*k),fill=fill)
  d.rounded_rectangle((.5*k,.5*k,(w-.5)*k,(h-.5)*k),radius=6*k,outline=edge,width=k)
 else:
  d.rounded_rectangle((.5*k,.5*k,(w-.5)*k,(h-.5)*k),radius=6*k,fill=fill,outline=edge,width=k)
  if kind not in ('field','status'):
   # Decoration lives within the 8px slicing border; center stays flat.
   light,dark=('#46484b','#212325') if disabled else ('#727478','#18191b')
   if pressed:light,dark=dark,light
   d.line((7*k,2*k,(w-7)*k,2*k),fill=light,width=k)
   d.line((7*k,(h-2)*k,(w-7)*k,(h-2)*k),fill=dark,width=k)
  if focused:d.rounded_rectangle((1*k,1*k,(w-1)*k,(h-1)*k),radius=6*k,outline='#85b4ff',width=2*k)
 return encode(im.resize((w,h),Image.Resampling.LANCZOS))
tiles={}
for name,(fill,edge,active,pressed) in palettes.items():
 for state,c,b,focus in [('normal',fill,edge,False),('active',active,edge,False),('pressed',pressed,edge,False),('disabled','#2a2b2e','#404246',False),('focus',fill,'#85b4ff',True),('focus_active',active,'#85b4ff',True)]:
  tiles[name+'_'+state]=tile(c,b,focus,kind=name,pressed=state=='pressed',disabled=state=='disabled')
tiles.update(field_normal=tile('#1c1d20','#45474b',kind='field'),field_disabled=tile('#2a2b2e','#404246',kind='field'),field_focus=tile('#1c1d20','#85b4ff',True,kind='field'),card=tile('#242528','#45474b',kind='card'),nav=tile('#17181a','#17181a',kind='nav'),status=tile('#3a3c40','#3a3c40',kind='status'))
im=Image.new('RGBA',(56,56));d=ImageDraw.Draw(im)
d.rounded_rectangle((19,3,51,35),radius=5,outline='#afb1b6',width=4);d.rounded_rectangle((4,18,36,50),radius=5,outline='#afb1b6',width=4)
tiles['popup_icon']=encode(im.resize((14,14),Image.Resampling.LANCZOS))
for action,color in (('defect','#f3a3ac'),('rotate','#c1d5ee')):
 for disabled in (False,True):
  color_now='#8c8e92' if disabled else color
  im=Image.new('RGBA',(64,64));d=ImageDraw.Draw(im)
  if action=='defect':
   d.line([(32,7),(58,54),(6,54),(32,7)],fill=color_now,width=6,joint='curve')
   d.line((32,24,32,36),fill=color_now,width=6);d.ellipse((29,42,35,48),fill=color_now)
  else:
   d.arc((10,10,54,54),205,360,fill=color_now,width=6)
   d.arc((10,10,54,54),25,180,fill=color_now,width=6)
   d.polygon([(54,16),(54,35),(38,28)],fill=color_now)
   d.polygon([(10,48),(10,29),(26,36)],fill=color_now)
  tiles[action+'_icon'+('_disabled' if disabled else '')]=encode(im.resize((16,16),Image.Resampling.LANCZOS))
node=nodes['_TILE_DATA'];lines=s.splitlines(True);lines[node.lineno-1:node.end_lineno]=['_TILE_DATA = '+repr(tiles)+'\n'];P.write_text(''.join(lines),encoding='utf-8')
# Switch dimensions and text hit area unchanged.
switches={}
for on in (False,True):
 im=Image.new('RGBA',(352,128));d=ImageDraw.Draw(im)
 d.rounded_rectangle((2,2,350,126),radius=62,fill='#203657' if on else '#313336',outline='#63666b' if on else '#585b60',width=4)
 x=70 if on else 18;d.ellipse(((x-13)*4,3*4,(x+13)*4,29*4),fill='#a7c9ff' if on else '#a9abaf')
 switches[on]=encode(im.resize((88,32),Image.Resampling.LANCZOS))
# Switch PNGs live in assets/; tools/build_app.py embeds them into app.pyw.
for on in (False,True):(R/'assets'/('alert_switch_on.png' if on else 'alert_switch_off.png')).write_bytes(base64.b64decode(switches[on]))
print('Generated',len(tiles),'assets; no runtime rendering or dependency added')
