"""Build the standalone dark portfolio concept. Run with Blender --background --python."""
import bpy, math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parent.parent
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0, roughness=.4, emission=0):
    m = bpy.data.materials.new(name); m.diffuse_color = (*color, 1); m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    p.inputs['Emission Color'].default_value = (*color, 1)
    p.inputs['Emission Strength'].default_value = emission
    return m

graphite = material('Obsidian / anodized alloy', (.022,.032,.052), .72, .28)
edge = material('Brushed titanium', (.10,.15,.20), .8, .3)
black = material('Screen / midnight glass', (.003,.009,.018), .35, .24)
cyan = material('Ion cyan', (.015,.72,1), .25, .25, 4)
violet = material('Ultraviolet', (.38,.045,1), .2, .3, 3)
white = material('Interface / ice', (.55,.85,1), .1, .4, 1.2)
muted = material('Interface / muted', (.06,.20,.32), .3, .4, .6)
floor = material('Backdrop', (.006,.009,.019), .25, .5)

def finish(o, name, mat):
    o.name = name; o.data.materials.append(mat)
    return o

def box(name, loc, size, mat, bevel=.035):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object; o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        m = o.modifiers.new('Machined radii', 'BEVEL'); m.width = bevel; m.segments = 3
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return finish(o, name, mat)

def cylinder(name, loc, radius, depth, mat, vertices=96):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o = finish(bpy.context.object, name, mat)
    b = o.modifiers.new('Rim radius', 'BEVEL'); b.width=.035; b.segments=3
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def ring(name, loc, radius, tube, mat, rot=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_segments=96, minor_segments=8, location=loc, major_radius=radius, minor_radius=tube, rotation=rot)
    o=finish(bpy.context.object,name,mat)
    for p in o.data.polygons: p.use_smooth=True
    return o

def text(name, body, loc, size, mat, rot=(math.pi/2,0,0)):
    bpy.ops.object.text_add(location=loc, rotation=rot)
    o=bpy.context.object; o.name=name; o.data.body=body; o.data.size=size
    o.data.extrude=.0005; o.data.materials.append(mat)
    return o

# Floating, layered landing pad. All visible geometry exports with its materials.
cylinder('Landing pad / lower shell', (0,0,.12), 3.05,.25,graphite)
cylinder('Landing pad / cyan seam', (0,0,.265), 3.015,.025,cyan)
cylinder('Landing pad / upper shell', (0,0,.34), 3.06,.12,graphite)
ring('Inset circular track', (0,0,.407), 2.85,.012,muted)
for i in range(48):
    a=i*math.tau/48
    o=box('Radial index %02d'%i,(2.72*math.cos(a),2.72*math.sin(a),.41),(.09,.018,.008),cyan if i%6==0 else muted,.003)
    o.rotation_euler.z=a
box('Desk slab',(0,0,.62),(4.45,2.1,.20),graphite,.1)
box('Desk / illuminated front edge',(0,-1.044,.62),(4.1,.015,.022),cyan,.007)
for x in [-1.65,1.65]:
    box('Desk standoff',(x,.2,.48),(.18,1.2,.3),edge)

# Laptop base, individual key caps and raised display.
box('Laptop chassis__projects',(-.35,-.15,.80),(2.55,1.55,.13),edge,.07)
box('Keyboard well',(-.35,-.03,.87),(2.22,.85,.015),black,.04)
for row in range(4):
    for col in range(13):
        box('Key %d %d'%(row,col),(-1.36+col*.168,-.32+row*.18,.895),(.126,.123,.025),graphite,.012)
box('Spacebar',(-.35,-.48,.894),(.78,.07,.026),muted,.01)
box('Trackpad',(-.35,-.70,.875),(.75,.25,.008),graphite,.025)
box('Laptop front status',(.58,-.929,.815),(.17,.008,.018),cyan,.004)
box('Display housing__projects',(-.35,.56,1.72),(2.56,.13,1.69),graphite,.075)
box('Display active area',(-.35,.486,1.72),(2.36,.018,1.47),black,.035)
text('Screen / title','SHANK /',(-1.38,.468,2.17),.20,white)
text('Screen / subtitle','BUILDING WHAT IS NEXT',(-1.37,.466,1.99),.062,cyan)
box('Screen header divider',(-.35,.465,1.91),(2.02,.006,.009),muted,.002)
for row,w in enumerate([.78,1.31,1.08,.56,1.40,.94]):
    box('Code line %02d'%row,(-1.30+w/2,.46,1.78-row*.085),(w,.008,.018),[violet,cyan,muted,white,muted,cyan][row],.003)
text('Screen / footer','01   SELECTED WORK  >',(-1.36,.463,1.13),.062,white)

# Orbital sculpture: a recognizable signature independent of laptop details.
cylinder('Orbital dock',(1.55,.46,.80),.39,.16,edge)
ring('Dock light',(1.55,.46,.887),.32,.018,violet)
center=(1.55,.46,1.72)
ring('Orbit / inclined',center,.62,.019,cyan,(math.radians(65),.3,.25))
ring('Orbit / meridian',center,.48,.014,violet,(.3,math.radians(70),.2))
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.25,location=center)
core=finish(bpy.context.object,'Core__skills',edge)
wire=core.modifiers.new('Energy lattice','WIREFRAME');wire.thickness=.012
core.data.materials.clear();core.data.materials.append(cyan)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.135,location=center)
finish(bpy.context.object,'Core nucleus',violet)

# Floating portfolio panel and small supporting details.
box('Floating panel frame__about',(-2.12,.70,1.75),(.74,.08,1.16),edge,.055)
box('Floating panel glass',(-2.12,.651,1.75),(.65,.01,1.06),black,.02)
text('Panel title','SYSTEM',(-2.40,.637,2.10),.073,cyan)
for i in range(5):
    box('Panel bar %d'%i,(-2.29+i*.085,.635,1.62+i*.035),(.042,.008,.20+i*.07),cyan if i<3 else violet,.004)
text('Panel footer','ONLINE',(-2.40,.636,1.34),.065,white)
cylinder('Utility puck',(1.5,-.65,.8),.25,.16,graphite)
ring('Puck status',(1.5,-.65,.888),.18,.012,cyan)
for i in range(3):
    box('Data cartridge %d'%i,(-1.80,-.55+i*.19,.80),(.25,.12,.12),edge,.02)
    box('Data indicator %d'%i,(-1.80,-.615+i*.19,.80),(.12,.008,.024),violet,.003)
text('Pad designation','S H A N K  /  S T U D I O',(-1.35,-1.85,.414),.13,white,rot=(0,0,0))
text('Pad caption','PERSONAL SYSTEM     -     001',(-1.15,-2.10,.414),.064,muted,rot=(0,0,0))

# Minimal portal behind the desk, open enough to preserve the silhouette.
ring('Portal / outer alloy',(0,1.20,2.02),1.88,.067,edge,(math.pi/2,0,0))
ring('Portal / cyan inner seam',(0,1.20,2.02),1.79,.018,cyan,(math.pi/2,0,0))
for x in [-1.35,1.35]:
    box('Portal anchor',(x,1.2,.62),(.28,.4,.38),graphite)

# Export model without the stage, lights or camera.
(ROOT/'assets').mkdir(exist_ok=True)
(ROOT/'public/models').mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(ROOT/'public/models/futuristic-studio.glb'),export_format='GLB',use_selection=True,export_cameras=False,export_lights=False,export_apply=True)
box('Render stage',(0,0,-.45),(200,200,.15),floor,.0)

def aim(obj, point): obj.rotation_euler=(Vector(point)-obj.location).to_track_quat('-Z','Y').to_euler()
for name,loc,power,color,size in [
    ('Key / cool softbox',(1,-4,7),1500,(.53,.76,1),5),
    ('Violet rim',(4,3,5),1800,(.43,.12,1),4),
    ('Cyan rim',(-4,1,4),1400,(.07,.74,1),3),
    ('Front fill',(0,-6,3),500,(.7,.8,1),4)]:
    bpy.ops.object.light_add(type='AREA',location=loc)
    o=bpy.context.object;o.name=name;o.data.energy=power;o.data.color=color;o.data.shape='DISK';o.data.size=size;aim(o,(0,0,1))
bpy.ops.object.camera_add(location=(7,-11,7))
cam=bpy.context.object;cam.name='Hero camera';aim(cam,(0,0,1.3));cam.data.type='ORTHO';cam.data.ortho_scale=8.6
scene=bpy.context.scene;scene.camera=cam;scene.render.engine='CYCLES';scene.cycles.samples=32
scene.cycles.use_denoising=True
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.015,.022,.05,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.3
scene.render.resolution_x=1400;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(ROOT/'assets/futuristic-preview.png')
# Open directly in a clean camera composition with material colors.
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_perspective='CAMERA'
            area.spaces.active.overlay.show_overlays=False
            area.spaces.active.shading.type='MATERIAL'
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets/futuristic-studio.blend'))
bpy.ops.render.render(write_still=True)
print('FUTURISTIC_CONCEPT_COMPLETE')
