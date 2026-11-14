"""Customize the official Spring mesh; preserve the original head and hairstyle.

Run with the official source .blend already open, and auto-execution disabled.
Spring Rig (CC-BY) Blender Foundation | https://studio.blender.org
"""
import bpy,math,json,sys
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parent.parent
MAPS=ROOT/'assets/spring-source/spring/spring/char/spring/maps'
source_scene=bpy.context.scene
source_scene.frame_set(1)

# Use only artist-authored meshes; film rig widgets/cages and particles stay out.
names=['GEO-spring_head','GEO_spring_arms','GEO-spring_jacket','GEO-spring_pullover',
       'GEO_spring_pants','GEO_spring_boots.l','GEO_spring_boots.r',
       'GEO_spring_eye.l','GEO_spring_eye.r','GEO_spring_eyebrows','GEO_spring_eyelashes',
       'GEO_spring_hair_main','GEO_spring_hair_braided','GEO_spring_hair_ears','GEO_spring_hair_ponytail',
       'GEO_spring_hairband_main','GEO_spring_hairband_endpiece','GEO_spring_teeth_top','GEO_spring_teeth_bottom',
       'GEO_spring_gums_top','GEO_spring_gums_bottom','GEO_spring_pants_button']
for c in bpy.data.collections:c.hide_viewport=False
def reveal(lc):
    lc.exclude=False;lc.hide_viewport=False
    for c in lc.children:reveal(c)
reveal(bpy.context.view_layer.layer_collection)
for n in names:
    o=bpy.data.objects.get(n)
    if not o:continue
    o.hide_set(False);o.hide_viewport=False
    for m in o.modifiers:
        if m.type=='SUBSURF':m.levels=2 if ('head' in n or 'hair' in n or 'eye' in n) else 1;m.render_levels=m.levels
        if m.type=='PARTICLE_SYSTEM':m.show_viewport=False;m.show_render=False

# Pose through the original FK controls before baking the deformation stack.
source_rig=bpy.data.objects['RIG-Spring']
for side,suffix in [(1,'L'),(-1,'R')]:
    props=source_rig.pose.bones.get('properties_arm_'+suffix)
    if props:props['ik_arm_'+suffix]=1.0
    p=source_rig.pose.bones['arm_fk_'+suffix]
    for c in p.constraints:
        if c.type=='COPY_TRANSFORMS':c.mute=True
    base=p.matrix.copy();pivot=base.translation.copy()
    p.matrix=Matrix.Translation(pivot) @ Matrix.Rotation(side*.55,4,'Y') @ Matrix.Translation(-pivot) @ base
bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get()
scene=bpy.data.scenes.new('Spring professional portrait')
collection=bpy.data.collections.new('SPRING-WEB');scene.collection.children.link(collection)
snapshots=[]
for n in names:
    original=bpy.data.objects.get(n)
    if not original:continue
    evaluated=original.evaluated_get(dg)
    raw=bpy.data.meshes.new_from_object(evaluated,preserve_all_data_layers=False,depsgraph=dg)
    # Retain the evaluated surface and UVs, without thousands of obsolete film-rig
    # weight/attribute layers. This leaves the artist's sculpt unchanged.
    data=bpy.data.meshes.new(n+' web surface')
    data.from_pydata([v.co for v in raw.vertices],[],[list(p.vertices) for p in raw.polygons])
    for m in raw.materials:data.materials.append(m)
    indices=[p.material_index for p in raw.polygons];data.polygons.foreach_set('material_index',indices)
    for layer in raw.uv_layers:
        dst=data.uv_layers.new(name=layer.name);values=[0.0]*(len(layer.data)*2)
        layer.data.foreach_get('uv',values);dst.data.foreach_set('uv',values)
    if raw.uv_layers.active:data.uv_layers.active_index=raw.uv_layers.active_index
    data.transform(original.matrix_world)
    bpy.data.meshes.remove(raw)
    # Relax the baked sleeves/arms to a standing presentation pose. Head and hair
    # are never part of this operation.
    if n in ['GEO-spring_jacket','GEO-spring_pullover','GEO_spring_arms']:
        for v in data.vertices:
            p=v.co.copy();side=1 if p.x>=0 else -1
            w=max(0,min(1,(abs(p.x)-.115)/.11));w=w*w*(3-2*w)
            h=max(0,min(1,(p.z-.73)/.13));h=h*h*(3-2*h)
            w*=h if abs(p.x)<.23 else 1
            pivot=Vector((side*.107,.015,.982))
            v.co=p.lerp(pivot+Matrix.Rotation(side*.72,3,'Y') @ (p-pivot),w)
    o=bpy.data.objects.new('Spring '+n+'__profile',data);collection.objects.link(o)
    o['spring_original_mesh']=n
    for p in data.polygons:p.use_smooth=True
    snapshots.append(o)
    print('BAKED',n,len(data.vertices),flush=True)
bpy.context.window.scene=scene
# Source data is baked. Remove the legacy control rig and helper objects from this
# working copy so they cannot be picked up by the glTF exporter's object scan.
keep={o.as_pointer() for o in snapshots}
for o in list(bpy.data.objects):
    if o.as_pointer() not in keep:bpy.data.objects.remove(o,do_unlink=True)
for action in list(bpy.data.actions):bpy.data.actions.remove(action)

def material(name,color,rough=.5,metal=0,image=None):
    m=bpy.data.materials.new(name);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    if image:
        path=MAPS/image
        im=bpy.data.images.load(str(path),check_existing=True)
        if max(im.size)>2048:im.scale(2048,2048)
        im.pack();tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im
        m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color'])
    return m
skin=material('Spring / original painted face',(1,1,1),.53,image='TEX_spring_head_color.png')
skin.node_tree.nodes['Principled BSDF'].inputs['Subsurface Weight'].default_value=.05
hands=material('Spring / original hand paint',(1,1,1),.55,image='TEX_spring_hands_color.png')
navy=material('Professional navy wool',(.016,.031,.061),.78)
lapelmat=material('Navy lapel weave',(.023,.046,.084),.74)
ivory=material('Ivory blouse',(.83,.82,.75),.77)
trousers=material('Charcoal tailored trousers',(.028,.034,.047),.80)
boots=material('Polished dark footwear',(.012,.017,.023),.34)
hair=material('Spring / dark brown mesh hair',(.025,.014,.010),.40)
brows=material('Spring / original brows',(.045,.022,.010),.68)
white=material('Spring / eye white',(.86,.83,.75),.25)
iris=material('Spring / original eye texture',(1,1,1),.26,image='TEX_spring_eyes_color.png')
pupil=material('Spring / pupil',(.002,.003,.004),.18)
enamel=material('Spring / enamel',(.80,.75,.65),.35)
mouth=material('Spring / mouth',(.12,.025,.023),.7)
metal=material('Graphite spectacle frames',(.032,.042,.056),.30,.7)
buttonmat=material('Subtle silver buttons',(.22,.25,.28),.33,.65)

def replacement(oldname,objectname):
    if 'eyes_white' in oldname:return white
    if 'eyes_iris' in oldname:return iris
    if 'eyes_pupil' in oldname:return pupil
    if 'mouth_inside' in oldname or 'gums' in oldname:return mouth
    if 'teeth' in oldname:return enamel
    if 'hair_eyebrow' in oldname or 'hair_eyelash' in oldname:return brows
    if 'MAT_spring_hair' in oldname:return hair
    if 'eyebrow' in objectname or 'eyelash' in objectname:return brows
    if 'hair' in objectname:return navy if 'hairband' in objectname else hair
    if 'head' in objectname:return skin
    if 'arms' in objectname:return hands
    if 'jacket' in objectname:return navy
    if 'pullover' in objectname:return ivory
    if 'pants_button' in objectname:return buttonmat
    if 'pants' in objectname:return trousers
    if 'boots' in objectname:return boots
    return navy
for o in snapshots:
    for i,m in enumerate(o.data.materials):o.data.materials[i]=replacement(m.name if m else '',o['spring_original_mesh'])

# Tailored blouse insert and lapels fitted over the existing coat (no face edits).
def panel(name,vertices,faces,mat):
    d=bpy.data.meshes.new(name);d.from_pydata(vertices,[],faces);d.update()
    o=bpy.data.objects.new(name+'__profile',d);collection.objects.link(o);d.materials.append(mat)
    solid=o.modifiers.new('Tailoring thickness','SOLIDIFY');solid.thickness=.0015
    bevel=o.modifiers.new('Soft stitched edge','BEVEL');bevel.width=.001;bevel.segments=2
    snapshots.append(o);return o
panel('Ivory V blouse insert',[(-.044,-.112,1.014),(.044,-.112,1.014),(.022,-.157,.870),(0,-.160,.815),(-.022,-.157,.870)],[(0,4,3,2,1)],ivory)
for side in [-1,1]:
    panel('Blazer notched lapel',[(side*.045,-.119,1.017),(side*.095,-.126,.981),(side*.068,-.158,.944),(side*.078,-.162,.927),(side*.010,-.169,.826),(side*.033,-.158,.924)],[(0,1,2,3,4,5)] if side>0 else [(5,4,3,2,1,0)],lapelmat)
    panel('Blouse collar',[(side*.010,-.108,1.022),(side*.045,-.119,1.014),(side*.038,-.141,.975)],[(0,1,2)] if side>0 else [(2,1,0)],ivory)

def curve(name,points,r,mat):
    d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.bevel_depth=r;d.bevel_resolution=2;d.resolution_u=12
    s=d.splines.new('BEZIER');s.bezier_points.add(len(points)-1)
    for v,co in zip(s.bezier_points,points):v.co=co;v.handle_left_type='AUTO';v.handle_right_type='AUTO'
    o=bpy.data.objects.new(name+'__profile',d);collection.objects.link(o);d.materials.append(mat)
    snapshots.append(o);return o
for side in [-1,1]:
    pts=[]
    for j in range(49):
        a=j*math.tau/48;dx=side*(.052+.051*math.cos(a))
        pts.append((dx,-.185+.025*(abs(dx)/.110)**2,1.206+.029*math.sin(a)))
    curve('Fine oval glasses rim',pts,.00155,metal)
    curve('Glasses temple',[(side*.102,-.164,1.209),(side*.139,-.102,1.209),(side*.145,-.027,1.202)],.00135,metal)
curve('Glasses bridge',[(-.009,-.185,1.210),(0,-.190,1.219),(.009,-.185,1.210)],.0014,metal)
for z in [.795,.743]:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=1,location=(.012,-.171,z))
    o=bpy.context.object;o.name='Blazer button__profile';o.scale=(.006,.002,.006);o.data.materials.append(buttonmat)
    for c in list(o.users_collection):c.objects.unlink(o)
    collection.objects.link(o);snapshots.append(o)

# Commit tailoring modifiers/curves, retaining all original artist-authored vertices.
for o in list(snapshots):
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    if o.type=='CURVE':bpy.ops.object.convert(target='MESH')
    for mod in list(o.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)

# Two-bone web rig: original deformation baked; subtle head idle without film controls.
data=bpy.data.armatures.new('Spring lightweight web skeleton');rig=bpy.data.objects.new('Spring professional web rig',data);collection.objects.link(rig)
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
rootbone=data.edit_bones.new('root');rootbone.head=(0,0,0);rootbone.tail=(0,0,.25)
headbone=data.edit_bones.new('head');headbone.head=(0,-.004,1.023);headbone.tail=(0,-.007,1.37);headbone.parent=rootbone
bpy.ops.object.mode_set(mode='OBJECT')
for o in snapshots:
    mw=o.matrix_world.copy();o.parent=rig;o.matrix_world=mw
    headpart=any(k in o.name.lower() for k in ['head','eye','hair','glasses'])
    b='head' if headpart else 'root'
    vg=o.vertex_groups.new(name=b);vg.add(list(range(len(o.data.vertices))),1,'REPLACE')
    mod=o.modifiers.new('Web idle skin','ARMATURE');mod.object=rig
scene.frame_start=1;scene.frame_end=121;scene.render.fps=30
for frame in range(1,122,4):
    t=(frame-1)/120*math.tau;p=rig.pose.bones['head'];p.rotation_mode='XYZ';p.rotation_euler=(.008*math.sin(t),.015*math.sin(t),.012*math.sin(t));p.keyframe_insert('rotation_euler',frame=frame)
rig.animation_data.action.name='Spring gentle idle';scene.frame_set(1)
rig['attribution']='Spring Rig (CC-BY) Blender Foundation | studio.blender.org'
rig['modifications']='Glasses, professional attire, baked web rig, materials adapted for glTF'
bpy.ops.object.select_all(action='DESELECT')
for o in [rig,*snapshots]:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'public/models/spring-professional.glb'),export_format='GLB',use_selection=True,export_apply=True,export_animations=True,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)

# Neutral portrait lighting, with no change to the original sculpt or hair silhouette.
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.resolution_x=1000;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Spring portrait background');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.07,.10,.14,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
for name,loc,power,color,size in [('Portrait key',(-2,-3,4),250,(1,.91,.82),3),('Portrait fill',(2,-2,2),130,(.83,.90,1),3),('Portrait rim',(1,2,3),200,(.65,.8,1),2)]:
    bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.name=name;l.data.energy=power;l.data.color=color;l.data.size=size
    l.rotation_euler=(Vector((0,0,.95))-l.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(1.15,-3.7,1.55));cam=bpy.context.object;scene.camera=cam
cam.rotation_euler=(Vector((0,-.02,.95))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1.54
scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.filepath=str(ROOT/'assets/spring-professional-preview.png')
for screen in bpy.data.screens:
    for a in screen.areas:
        if a.type=='VIEW_3D':a.spaces.active.region_3d.view_perspective='CAMERA';a.spaces.active.overlay.show_overlays=False
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets/spring-professional.blend'))
if '--no-render' not in sys.argv:bpy.ops.render.render(write_still=True)
cam.location=(0,-3.7,1.35);cam.rotation_euler=(Vector((0,-.025,1.15))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.72
scene.render.filepath=str(ROOT/'assets/spring-professional-face.png')
if '--no-render' not in sys.argv:bpy.ops.render.render(write_still=True)
print('SPRING_CUSTOMIZATION_COMPLETE')
