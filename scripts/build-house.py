"""Editable cutaway cyberpunk home; retains the original personal character."""
import bpy, math, sys, random, json
from pathlib import Path
from mathutils import Vector, Matrix
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
from avatar import build_avatar
random.seed(8)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)

def mat(name,c,metal=0,glow=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1)
    p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=.46
    p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=glow
    return m
wall=mat('Midnight teal plaster',(.024,.075,.09));dark=mat('Graphite trim',(.018,.026,.04),.5)
wood=mat('Warm walnut',(.19,.075,.038));wood2=mat('Walnut end grain',(.29,.13,.065))
cyan=mat('Electric cyan',(.015,.7,.86),.2,3);purple=mat('Lavender neon',(.49,.09,.85),.2,2)
amber=mat('Warm lamplight',(1,.47,.13),0,2);paper=mat('Ivory paper',(.69,.76,.69))
blue=mat('Indigo fabric',(.058,.065,.16));green=mat('Plant leaves',(.045,.25,.17));pink=mat('Rose accent',(.53,.08,.22))
metal=mat('Brushed steel',(.13,.21,.25),.75);glass=mat('Night window',(.007,.026,.07),.65)

def done(o,name,m):
    o.name=name;o.data.materials.append(m);return o
def box(name,loc,size,m,b=.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.scale=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if b:
        mod=o.modifiers.new('Soft edges','BEVEL');mod.width=b;mod.segments=2
        o.modifiers.new('Normals','WEIGHTED_NORMAL')
    return done(o,name,m)
def cyl(name,loc,r,d,m):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=d,location=loc)
    return done(bpy.context.object,name,m)
def ball(name,loc,scale,m):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=loc)
    o=bpy.context.object;o.scale=scale
    for p in o.data.polygons:p.use_smooth=True
    return done(o,name,m)
def text(name,body,loc,size,m,rot=(math.pi/2,0,0),font=None):
    bpy.ops.object.text_add(location=loc,rotation=rot);o=bpy.context.object;o.name=name
    o.data.body=body;o.data.size=size;o.data.extrude=.001;o.data.materials.append(m)
    if font:o.data.font=font
    bpy.ops.object.convert(target='MESH');return bpy.context.object
def line(name,pts,m,r=.018):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=2
    s=c.splines.new('POLY');s.points.add(len(pts)-1)
    for p,v in zip(s.points,pts):p.co=(*v,1)
    o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);o.data.materials.append(m)
    return o
def plant(x,y,z,scale=1):
    cyl('Ceramic planter',(x,y,z+.22*scale),.22*scale,.44*scale,wood2)
    for i in range(7):
        a=i*2.4;h=(.65+(i%3)*.13)*scale
        line('Plant stem',[(x,y,z+.3*scale),(x+.22*math.cos(a)*scale,y+.22*math.sin(a)*scale,z+h)],green,.015*scale)
        o=ball('Sculpted leaf',(x+.21*math.cos(a)*scale,y+.21*math.sin(a)*scale,z+h),(.10*scale,.06*scale,.25*scale),green)
        o.rotation_euler=(.5*math.cos(a),.5*math.sin(a),a)

# A recognizable gabled home, opened at the front and right to reveal the rooms.
box('Floating house foundation',(0,-.25,.15),(10.3,8.0,.35),dark,.18)
box('Foundation cyan reveal',(0,-.25,.33),(10.1,7.82,.035),cyan,.01)
box('House flooring',(0,0,.43),(9.2,6.1,.17),wood,.06)
for i in range(23):box('Floorboard seam',(-4.4+i*.4,0,.522),(.012,5.95,.006),wood2,.0)
box('Rear wall',(0,2.95,2.50),(9.2,.18,4.05),wall)
box('West wall',(-4.51,0,2.50),(.18,6,4.05),wall)
box('East cutaway wall',(4.51,.15,1.02),(.18,5.7,1.12),wall)
for x in [-4.4,4.4]:box('Structural corner',(x,2.79,2.52),(.17,.16,4.1),dark)
for z in [.61,4.42]:box('Rear architectural trim',(0,2.82,z),(9,.10,.10),wood2)
# Rear roof portion and front open gable make the cutaway readable.
for side in [-1,1]:
    o=box('Rear roof',(side*2.27,2.44,5.13),(5.05,1.55,.17),dark)
    o.rotation_euler.y=side*math.radians(19)
    line('Open gable beam',[(0,-2.89,5.91),(side*4.72,-2.89,4.30)],wood2,.075)
    line('Neon gable outline',[(0,-2.93,5.96),(side*4.72,-2.93,4.35)],cyan,.018)
    box('Eave edge',(side*4.6,0,4.37),(.14,6.2,.14),dark)
box('Front sign beam',(0,-2.9,4.27),(9.45,.16,.18),wood2)
box('House nameplate',(0,-3.01,4.26),(3.10,.10,.50),dark,.06)
house_title=text('House title / Shanks Studio','SHANKS STUDIO',(0,-3.075,4.14),.29,cyan)
title_left=min(v.co.x for v in house_title.data.vertices);title_right=max(v.co.x for v in house_title.data.vertices)
house_title.scale*=min(1,2.78/(title_right-title_left))
house_title.location.x-=(title_left+title_right)/2*house_title.scale.x
box('Welcome porch',(0,-3.47,.45),(9.2,.85,.18),wood)
for i in range(3):box('Entry step',(2.6,-4.13-i*.25,.34-i*.11),(2.3,.5,.16),dark,.05)
for i in range(15):
    x=-4.15+i*.59;z=3.96-.22*(1-(x/4.3)**2)
    ball('Stringlight %02d'%i,(x,-2.91,z),(.046,.046,.075),amber)
line('String light cable',[(-4.3+i*.215,-2.91,3.96-.22*(1-((-4.3+i*.215)/4.3)**2)) for i in range(41)],dark,.013)

# Project cupboard: real hinged doors, each project lives as an artifact on a shelf.
cx=-2.7
for x in [cx-1.0,cx+1.0]:box('Cupboard side__projects',(x,2.13,1.86),(.12,1.05,2.65),wood)
box('Cupboard back__projects',(cx,2.61,1.86),(2.1,.10,2.65),dark)
for z in [.59,1.40,2.23,3.18]:box('Cupboard shelf__projects',(cx,2.13,z),(2.10,1.08,.10),wood2)
for z in [1.44,2.27,3.22]:box('Shelf lighting__projects',(cx,1.62,z),(1.85,.025,.022),cyan,.005)
text('Cupboard label','THE PROJECT ARCHIVE',(cx-.98,1.54,3.44),.125,cyan)
for side in [-1,1]:
    hinge=bpy.data.objects.new('cupboard_hinge_'+('L' if side<0 else 'R'),None);bpy.context.collection.objects.link(hinge)
    hinge.location=(cx+side*1.04,1.55,1.87)
    parts=[box('Cupboard door__projects',(cx+side*.52,1.55,1.87),(1.01,.10,2.52),wood,.045),
           box('Inset door panel__projects',(cx+side*.52,1.484,1.87),(.80,.025,2.28),wall,.035),
           box('Door handle__projects',(cx+side*.12,1.43,1.87),(.045,.06,.32),cyan,.012)]
    for o in parts:mw=o.matrix_world.copy();o.parent=hinge;o.matrix_world=mw
portfolio=json.loads((ROOT/'src/portfolio-content.json').read_text(encoding='utf8'))
label_ink=mat('Project label ink',(.001,.001,.001))
label_shader=label_ink.node_tree.nodes.get('Principled BSDF')
label_shader.inputs['Specular IOR Level'].default_value=0
label_stock=mat('Project labels / matte sage',(.34,.38,.35))
project_shell=mat('Project boxes / matte charcoal',(.018,.027,.033))
for material in [label_stock,project_shell]:
    shader=material.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Roughness'].default_value=.95;shader.inputs['Specular IOR Level'].default_value=0
font_paths=[Path('C:/Windows/Fonts/seguisb.ttf'),Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')]
font_path=next((p for p in font_paths if p.exists()),None)
label_font=bpy.data.fonts.load(str(font_path)) if font_path else None
for i,name in enumerate(portfolio['projectOrder']):
    project=portfolio['projects'][name]
    z=2.40-(i//3)*.86;x=cx-.65+(i%3)*.65
    box('Project cartridge__'+name,(x,2.05,z+.20),(.56,.5,.42),project_shell,.05)
    box('Project label plate__'+name,(x,1.785,z+.20),(.46,.022,.26),label_stock,.018)
    label=text('Cartridge title__'+name,project['shelfLabel'],(x,1.752,z+.18),.08,label_ink,font=label_font)
    low=min(v.co.x for v in label.data.vertices);high=max(v.co.x for v in label.data.vertices)
    label.scale*=min(1,.41/(high-low))
    label.location.x-=(low+high)/2*label.scale.x

# Skills workstation, with a glowing terminal and small drawers.
box('Workbench__skills',(1.65,2.05,1.45),(3.35,1.28,.14),wood2,.05)
for x in [.23,3.05]:box('Workbench leg__skills',(x,2.1,.95),(.15,.90,.9),dark)
box('Monitor stand__skills',(1.65,2.22,1.65),(.13,.18,.5),metal)
box('Terminal frame__skills',(1.65,2.30,2.25),(1.95,.13,1.14),dark,.06)
box('Terminal glass__skills',(1.65,2.223,2.25),(1.76,.015,.96),glass)
text('Terminal heading__skills','> SKILLS.EXE',(.89,2.207,2.50),.14,cyan)
for i,(s,m) in enumerate([('JAVA / SPRING BOOT',paper),('AZURE / .NET / APIs',purple),('CLOUD INTEGRATION',cyan)]):text('Terminal line__skills',s,(.89,2.207,2.27-i*.17),.08,m)
box('Keyboard__skills',(1.6,1.75,1.56),(1.3,.38,.06),dark)
for i in range(12):box('Keyboard key',(1.06+i*.095,1.72,1.601),(.06,.25,.012),metal,.004)
cyl('Desk mug',(2.80,1.8,1.73),.12,.3,wood2)
box('Chair seat',(1.65,.70,1.0),(.85,.75,.16),blue,.12)
box('Chair back',(1.65,1.04,1.47),(.85,.14,.9),blue,.12)
for x in [1.35,1.95]:
    for y in [.45,.96]:box('Chair leg',(x,y,.72),(.07,.07,.5),wood)

# Life timeline integrated into the rear wall above the desk.
for i in range(3):
    x=.35+i*1.19
    box('Memory frame__experience',(x,2.80,3.55),(.97,.10,.82),wood2)
    box('Memory print__experience',(x,2.737,3.55),(.82,.012,.68),blue if i%2 else glass)
    text('Memory number__experience','0'+str(i+1),(x-.30,2.72,3.58),.19,purple if i==1 else cyan)
    text('Memory caption__experience',['LEARN','BUILD','GROW'][i],(x-.30,2.72,3.36),.074,paper)

# Cozy domestic details: sofa, rug, table, books, wall art, plants.
box('Lounge rug',(-.4,-.8,.535),(4.4,2.25,.025),blue,.15)
for x in [-2.52,1.72]:box('Rug border',(x,-.8,.552),(.03,2.05,.009),purple,.003)
box('Sofa plinth',(-2.77,-.42,.80),(2.5,1.0,.40),wood)
box('Sofa back',(-2.77,.02,1.25),(2.5,.20,.94),blue,.12)
for x in [-3.88,-1.65]:box('Sofa arm',(x,-.44,1.14),(.24,1.05,.6),blue,.1)
for x in [-3.30,-2.28]:box('Seat cushion',(x,-.43,1.01),(.93,.80,.23),blue,.1)
o=box('Accent cushion',(-3.31,-.08,1.42),(.48,.18,.44),pink,.1);o.rotation_euler.y=.20
box('Coffee table',(-.40,-.91,.96),(1.48,.82,.10),wood2,.12)
for x in [-.90,.10]:box('Coffee table leg',(x,-.91,.74),(.10,.50,.46),dark)
box('Open notebook__about',(-.52,-1.02,1.03),(.50,.36,.035),paper,.01)
cyl('Tea cup',(.03,-.79,1.13),.10,.18,wood2)
for i in range(2):
    z=2.15+i*.94
    box('Bookshelf__education',(-4.10,.3,z),(.65,2.1,.10),wood2)
    for j in range(7):box('Book spine__education',(-4.08,-.48+j*.23,z+.22+(.03*(j%3))),(.42,.15,.35+.06*(j%3)),[blue,paper,purple,wood][j%4],.008)
box('Window frame',(-4.39,1.9,3.06),(.12,1.22,1.7),wood2)
box('Window glow',(-4.31,1.9,3.06),(.035,1.08,1.55),glass)
for z in [2.35,3.05,3.75]:box('Window horizontal',(-4.27,1.9,z),(.04,1.11,.035),cyan,.008)
plant(3.72,2.20,.53,1.5);plant(-3.90,-2.20,.53,1.1);plant(3.82,-2.10,.53,1.3)
box('Porch bench',(-.70,-3.37,1.20),(1.65,.68,.16),wood2,.06)
for x in [-1.30,-.10]:box('Bench leg',(x,-3.37,.85),(.1,.48,.6),dark)

# Original fully modeled reference-inspired character, seated on the porch.
rig,meshes=build_avatar(ROOT)
if rig.get('attribution'):
    rig.location+=Vector((1.1,-3.35,.52))
else:
    rig.matrix_world=Matrix.Translation(Vector((-.7,-3.35,.52))) @ Matrix.Rotation(math.pi,4,'Z') @ Matrix.Translation(Vector((.7,.7,0)))
rig.name='Shank / three dimensional porch character__about'

# Mailbox provides a memorable contact destination.
box('Mailbox post__contact',(3.87,-3.31,1.12),(.12,.12,1.2),wood2)
box('Mailbox__contact',(3.87,-3.31,1.83),(.67,.55,.47),wall,.09)
box('Mailbox slot__contact',(3.87,-3.60,1.87),(.44,.015,.055),cyan,.01)
text('Mail label__contact','SAY HELLO',(3.58,-3.606,1.67),.075,paper)
box('Porch sign',(-3.65,-3.33,1.1),(.94,.09,.7),dark,.05)
text('Porch sign text','COME ON IN',(-4.05,-3.39,1.17),.10,cyan)
text('Porch sign sub','make yourself at home',(-4.05,-3.39,1.00),.052,paper)

# A separate asset without render-stage objects.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(ROOT/'public/models/cyber-home.glb'),export_format='GLB',use_selection=True,export_apply=True,export_animations=True,export_lights=False,export_cameras=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)

ground=mat('Night ground',(.006,.012,.023),.3)
box('Render ground',(0,0,-.25),(200,200,.12),ground,0)
for name,loc,power,color,size in [('Cool key',(2,-6,10),2200,(.45,.76,1),7),('Violet rim',(6,2,7),2500,(.52,.16,1),5),('Warm interior',(-2,0,5),800,(1,.6,.3),4),('Cyan fill',(-7,-3,5),1500,(.08,.8,1),5)]:
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name
    o.data.energy=power;o.data.color=color;o.data.shape='DISK';o.data.size=size
    o.rotation_euler=(Vector((0,0,1.5))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(12,-18,12));cam=bpy.context.object
cam.rotation_euler=(Vector((0,-.4,2.3))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=15
scene=bpy.context.scene;scene.camera=cam;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.world.color=(.025,.035,.06);scene.render.resolution_x=1500;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(ROOT/'assets/cyber-home-preview.png')
for screen in bpy.data.screens:
    for a in screen.areas:
        if a.type=='VIEW_3D':
            a.spaces.active.region_3d.view_perspective='CAMERA';a.spaces.active.overlay.show_overlays=False
            a.spaces.active.shading.type='MATERIAL'
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets/cyber-home.blend'))
if '--no-render' not in sys.argv:bpy.ops.render.render(write_still=True)
print('HOUSE_COMPLETE')
