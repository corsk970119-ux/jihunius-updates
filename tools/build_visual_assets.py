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
 k=4;w,h=128,64;im=Image.new('RGBA',(w*k,h*k),'#060b16' if kind in ('popup','popup_open','handover','handover_notice','tab','tab_selected','nav') else '#060b16');d=ImageDraw.Draw(im)
 bg='#060b16'
 if kind in ('card','tab','tab_selected','popup','popup_open','handover','handover_notice','nav'):d.rectangle((0,0,w*k,h*k),fill=bg)
 if kind=='nav':
  d.rectangle((0,0,w*k,h*k),fill=fill)
 elif kind=='card':
  # N3: card is the window surface with one crisp 1px outline and 4px corners.
  d.rounded_rectangle((.5*k,.5*k,(w-.5)*k,(h-.5)*k),radius=4*k,fill=fill,outline=edge,width=k)
 elif kind in ('tab','tab_selected'):
  # Underline tabs: flat surface, 2px accent rule along the bottom when selected.
  d.rectangle((0,0,w*k,h*k),fill=fill)
  if edge!=fill:d.rectangle((0,(h-2)*k,w*k,h*k),fill=edge)
  if focused:d.rectangle((1*k,1*k,(w-1)*k,(h-3)*k),outline='#8db3ff',width=2*k)
 else:
  # Flat A-3a controls: one hairline border, no bevel.
  d.rounded_rectangle((.5*k,.5*k,(w-.5)*k,(h-.5)*k),radius=4*k,fill=fill,outline=edge,width=k)
  if focused:d.rounded_rectangle((1*k,1*k,(w-1)*k,(h-1)*k),radius=4*k,outline='#8db3ff',width=2*k)
 return encode(im.resize((w,h),Image.Resampling.LANCZOS))
tiles={}
for name,(fill,edge,active,pressed) in palettes.items():
 for state,c,b,focus in [('normal',fill,edge,False),('active',active,edge,False),('pressed',pressed,edge,False),('disabled','#0b1529','#22355c',False),('focus',fill,'#8db3ff',True),('focus_active',active,'#8db3ff',True)]:
  tiles[name+'_'+state]=tile(c,b,focus,kind=name,pressed=state=='pressed',disabled=state=='disabled')
tiles.update(field_normal=tile('#050a14','#2c4274',kind='field'),field_disabled=tile('#0b1529','#22355c',kind='field'),field_focus=tile('#050a14','#8db3ff',True,kind='field'),card=tile('#060b16','#2c4274',kind='card'),nav=tile('#060b16','#060b16',kind='nav'),status=tile('#0e1a35','#0e1a35',kind='status'))
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
# N3 section heading marker: 4x14 accent bar plus transparent gap before the text.
im=Image.new('RGBA',(12*4,14*4));d=ImageDraw.Draw(im);d.rectangle((0,0,4*4-1,14*4-1),fill='#8db3ff')
tiles['heading_bar']=encode(im.resize((12,14),Image.Resampling.LANCZOS))
# N3 work-mode radio marks (selected keeps the white dot, unselected a muted ring).
for key,ring,dot in (('radio_off','#7f93bd',None),('radio_on','#ffffff','#ffffff')):
 im=Image.new('RGBA',(22*4,16*4));d=ImageDraw.Draw(im)
 d.ellipse((1*4,1*4,15*4,15*4),outline=ring,width=2*4)
 if dot:d.ellipse((5*4,5*4,11*4,11*4),fill=dot)
 tiles[key]=encode(im.resize((22,16),Image.Resampling.LANCZOS))
node=nodes['_TILE_DATA'];lines=s.splitlines(True);lines[node.lineno-1:node.end_lineno]=['_TILE_DATA = '+repr(tiles)+'\n'];P.write_text(''.join(lines),encoding='utf-8')
# Switch dimensions and text hit area unchanged.
switches={}
for on in (False,True):
 im=Image.new('RGBA',(352,128));d=ImageDraw.Draw(im)
 d.rounded_rectangle((2,2,350,126),radius=62,fill='#2a66f2' if on else '#0f1a30',outline='#8db3ff' if on else '#3b5488',width=4)
 x=70 if on else 18;d.ellipse(((x-13)*4,3*4,(x+13)*4,29*4),fill='#ffffff' if on else '#aebcd8')
 switches[on]=encode(im.resize((88,32),Image.Resampling.LANCZOS))
# Switch PNGs live in assets/; tools/build_app.py embeds them into app.pyw.
for on in (False,True):(R/'assets'/('alert_switch_on.png' if on else 'alert_switch_off.png')).write_bytes(base64.b64decode(switches[on]))
print('Generated',len(tiles),'assets; no runtime rendering or dependency added')
