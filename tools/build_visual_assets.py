"""Build small flat ttk assets offline. Pillow is not used by the application."""
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
def tile(fill,edge,focused=False,kind='button'):
 k=4;w,h=128,64;im=Image.new('RGBA',(w*k,h*k),'#111722' if kind in ('popup','popup_open','handover','handover_notice','tab','tab_selected','nav') else '#1b2433');d=ImageDraw.Draw(im)
 if kind in ('tab','tab_selected'):
  d.rectangle((0,0,w*k,h*k),fill=fill)
  if kind=='tab_selected':d.rectangle((6*k,(h-2)*k,(w-6)*k,h*k),fill='#85b4ff')
  if focused:d.rectangle((1*k,1*k,(w-1)*k,(h-1)*k),outline='#85b4ff',width=k)
 elif kind=='nav':
  d.rectangle((0,0,w*k,h*k),fill=fill)
 elif kind=='card':
  d.rectangle((0,0,w*k,h*k),fill=fill)
  d.line((0,0,w*k,0),fill=edge,width=k)
 else:
  d.rounded_rectangle((.5*k,.5*k,(w-.5)*k,(h-.5)*k),radius=6*k,fill=fill,outline=edge,width=(2 if focused else 1)*k)
 return encode(im.resize((w,h),Image.Resampling.LANCZOS))
tiles={}
for name,(fill,edge,active,pressed) in palettes.items():
 for state,c,b,focus in [('normal',fill,edge,False),('active',active,edge,False),('pressed',pressed,edge,False),('disabled','#202b3b','#334157',False),('focus',fill,'#85b4ff',True),('focus_active',active,'#85b4ff',True)]:
  tiles[name+'_'+state]=tile(c,b,focus,kind=name)
tiles.update(field_normal=tile('#131c2b','#36455e'),field_disabled=tile('#202b3b','#334157'),field_focus=tile('#131c2b','#85b4ff',True),card=tile('#1b2433','#36455e',kind='card'),nav=tile('#111722','#111722',kind='nav'),status=tile('#2b3b52','#2b3b52'))
im=Image.new('RGBA',(56,56));d=ImageDraw.Draw(im)
d.rounded_rectangle((19,3,51,35),radius=5,outline='#a4b6cc',width=4);d.rounded_rectangle((4,18,36,50),radius=5,outline='#a4b6cc',width=4)
tiles['popup_icon']=encode(im.resize((14,14),Image.Resampling.LANCZOS))
node=nodes['_TILE_DATA'];lines=s.splitlines(True);lines[node.lineno-1:node.end_lineno]=['_TILE_DATA = '+repr(tiles)+'\n'];P.write_text(''.join(lines),encoding='utf-8')
# Switch dimensions and text hit area unchanged.
p=R/'apps/jihunius/app.pyw';s=p.read_text(encoding='utf-8');t=ast.parse(s)
node=next(n for n in t.body if isinstance(n,ast.Assign) and getattr(n.targets[0],'id','')=='MACHINE_ALERT_SWITCH_PNGS')
switches={}
for on in (False,True):
 im=Image.new('RGBA',(352,128));d=ImageDraw.Draw(im)
 d.rounded_rectangle((2,2,350,126),radius=62,fill='#203657' if on else '#263144',outline='#526782' if on else '#465c78',width=4)
 x=70 if on else 18;d.ellipse(((x-13)*4,3*4,(x+13)*4,29*4),fill='#a7c9ff' if on else '#a0aec3')
 switches[on]=encode(im.resize((88,32),Image.Resampling.LANCZOS))
lines=s.splitlines(True);lines[node.lineno-1:node.end_lineno]=['MACHINE_ALERT_SWITCH_PNGS = '+repr(switches)+'\n'];p.write_text(''.join(lines),encoding='utf-8')
print('Generated',len(tiles),'assets; no runtime rendering or dependency added')
