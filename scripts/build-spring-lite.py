"""Create a separate lightweight Spring variant from the approved detailed asset.

Spring Rig (CC-BY) Blender Foundation | https://studio.blender.org
The source .blend and detailed GLB are never overwritten.
"""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector,kdtree
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parent.parent
ASSETS=ROOT/'assets'
SOURCE=ASSETS/'spring-detailed.blend'
source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
scene=bpy.context.scene;scene.frame_set(1)
collection=bpy.data.collections['SPRING-WEB'];rig=next(o for o in collection.objects if o.type=='ARMATURE')

# One top and trousers: remove the undershirt, coat additions and hidden mouth parts.
remove_tokens=['GEO-spring_pullover','GEO_spring_boots.','GEO_spring_hair_braided',
               'GEO_spring_hair_ears',
               'GEO_spring_pants',
               'GEO_spring_hairband_endpiece','GEO_spring_teeth_','GEO_spring_gums_',
               'GEO_spring_pants_button','Ivory V blouse','Blazer notched lapel',
               'Blouse collar','Blazer button','Fine oval glasses rim','Glasses temple','Glasses bridge']
for o in list(collection.objects):
    if o.type=='MESH' and any(t in o.name for t in remove_tokens):bpy.data.objects.remove(o,do_unlink=True)

# Downsize each opaque color image once, using new files unique to this variant.
texture_dir=ASSETS/'spring-lite-textures';texture_dir.mkdir(exist_ok=True)
image_cache={}
processed_materials=set()
for o in collection.objects:
    if o.type!='MESH':continue
    for mat in o.data.materials:
        if not mat or not mat.use_nodes:continue
        if mat.as_pointer() in processed_materials:continue
        processed_materials.add(mat.as_pointer())
        for node in mat.node_tree.nodes:
            if node.type!='TEX_IMAGE' or not node.image:continue
            old=node.image
            if old.name not in image_cache:
                size=1024 if 'head_color' in old.name else 512
                image=old.copy();image.name=old.name+' lite'
                image.scale(size,size);image.file_format='JPEG'
                image.filepath_raw=str(texture_dir/(old.name.split('.')[0]+'-lite.jpg'))
                image.save()
                optimized=bpy.data.images.load(image.filepath_raw,check_existing=False);optimized.pack()
                image_cache[old.name]=optimized
            node.image=image_cache[old.name]

# Very dark brown irises, retaining the radial texture and separate black pupil.
# Store this in the texture itself so Blender and glTF show the same eye colour.
iris=next(m for m in bpy.data.materials if m.name.startswith('Spring / original eye texture'))
shader=iris.node_tree.nodes.get('Principled BSDF')
texture=shader.inputs['Base Color'].links[0].from_node
image=texture.image.copy();pixels=list(image.pixels[:])
for i in range(0,len(pixels),4):
    light=.2126*pixels[i]+.7152*pixels[i+1]+.0722*pixels[i+2]
    pixels[i]=light*.31;pixels[i+1]=light*.19;pixels[i+2]=light*.12
image.pixels.foreach_set(pixels);image.file_format='JPEG'
image.filepath_raw=str(texture_dir/'spring-dark-brown-irises.jpg');image.save()
texture.image=bpy.data.images.load(image.filepath_raw,check_existing=False);texture.image.pack()
iris.name='Spring / brown black eye texture'

# Protect the recognizable face with a higher budget than clothes and hidden parts.
def ratio_for(name):
    if 'GEO-spring_head' in name:return .30
    if 'GEO_spring_arms' in name:return .070
    if 'GEO-spring_jacket' in name:return .060
    if 'GEO_spring_pants' in name:return .080
    if 'GEO_spring_eye.' in name:return .065
    if 'GEO_spring_hair_main' in name:return .16
    if 'GEO_spring_hair_ponytail' in name:return .16
    if 'GEO_spring_hair_ears' in name:return .22
    if 'GEO_spring_hairband_main' in name:return .16
    if 'eyebrow' in name:return .35
    if 'eyelash' in name:return .30
    if 'glasses' in name.lower():return .60
    return .40
report=[]
for o in list(collection.objects):
    if o.type!='MESH':continue
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    armatures=[(m,m.show_viewport,m.show_render) for m in o.modifiers if m.type=='ARMATURE']
    for m,_,_ in armatures:m.show_viewport=False;m.show_render=False
    before=sum(len(p.vertices)-2 for p in o.data.polygons)
    dec=o.modifiers.new('Web silhouette budget','DECIMATE');dec.ratio=ratio_for(o.name);dec.use_collapse_triangulate=True
    # Apply simplification before skinning, with the bind pose unchanged.
    bpy.ops.object.modifier_move_up(modifier=dec.name)
    bpy.ops.object.modifier_apply(modifier=dec.name)
    for m,v,r in armatures:m.show_viewport=v;m.show_render=r
    for p in o.data.polygons:p.use_smooth=True
    after=sum(len(p.vertices)-2 for p in o.data.polygons)
    report.append({'name':o.name,'before':before,'after':after})

# Replace the tall boots with small flat shoes and a plain trouser cuff.
shoe=bpy.data.materials.new('Lite / matte navy flats');shoe.use_nodes=True
shader=shoe.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=(.012,.018,.026,1);shader.inputs['Roughness'].default_value=.60
pants=next(m for m in bpy.data.materials if m.name.startswith('Charcoal tailored trousers'))
top=next(m for m in bpy.data.materials if m.name.startswith('Professional navy wool'))

def attach(o,name,mat,bone='root'):
    o.name=name+'__profile'
    for c in list(o.users_collection):c.objects.unlink(o)
    collection.objects.link(o);o.data.materials.clear();o.data.materials.append(mat)
    mw=o.matrix_world.copy();o.parent=rig;o.matrix_world=mw
    vg=o.vertex_groups.new(name=bone);vg.add(list(range(len(o.data.vertices))),1,'REPLACE')
    mod=o.modifiers.new('Web idle skin','ARMATURE');mod.object=rig
    for p in o.data.polygons:p.use_smooth=True
    return o

# Slightly wider, rounder frames, retaining the original fine graphite finish.
# Match the bridge and temple tips to the new rims and keep them head-skinned.
metal=bpy.data.materials['Graphite spectacle frames']
def spectacle_curve(name,points,radius,cyclic=False):
    data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D'
    data.bevel_depth=radius;data.bevel_resolution=2;data.resolution_u=3
    spline=data.splines.new('BEZIER');spline.bezier_points.add(len(points)-1)
    for vertex,point in zip(spline.bezier_points,points):
        vertex.co=point;vertex.handle_left_type='AUTO';vertex.handle_right_type='AUTO'
    spline.use_cyclic_u=cyclic
    o=bpy.data.objects.new(name,data);collection.objects.link(o)
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    bpy.ops.object.convert(target='MESH')
    return attach(bpy.context.object,name,metal,'head')

def frame_depth(x):return -.185+.025*(abs(x)/.110)**2
for side in [-1,1]:
    points=[]
    for j in range(48):
        angle=j*math.tau/48;x=side*(.0555+.053*math.cos(angle))
        points.append((x,frame_depth(x),1.206+.042*math.sin(angle)))
    spectacle_curve('Round glasses rim',points,.00155,True)
    spectacle_curve('Glasses temple',[(side*.1085,frame_depth(.1085),1.206),(side*.139,-.102,1.209),(side*.145,-.027,1.202)],.00135)
bridge_x=.0555-.053*.90
bridge_z=1.206+.042*math.sqrt(1-.90**2)
spectacle_curve('Glasses bridge',[(-bridge_x,frame_depth(bridge_x),bridge_z),(0,-.190,bridge_z+.006),(bridge_x,frame_depth(bridge_x),bridge_z)],.0014)

# Short parted forehead sweeps follow the user's drawn reference. They are fitted
# to the original forehead/crown surface, with no long strands beside the cheeks.
hair=next(m for m in bpy.data.materials if m.name.startswith('Spring / dark brown mesh hair'))
surfaces=[o for o in collection.objects if o.type=='MESH' and any(s in o.name for s in ['GEO-spring_head','GEO_spring_hair_main'])]
trees=[BVHTree.FromPolygons([o.matrix_world @ v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons],all_triangles=False) for o in surfaces]
def forehead_surface(x,z):
    # Keep the upper temple edges within the head's actual silhouette. A nearest-
    # surface extrapolation here would create small floating points at the ends.
    for _ in range(35):
        hits=[tree.ray_cast(Vector((x,-1,z)),Vector((0,1,0)),2)[0] for tree in trees]
        visible=[hit for hit in hits if hit is not None]
        if visible:return x,min(hit.y for hit in visible)
        x=-.005+(x+.005)*.97
    raise RuntimeError('Could not fit fringe to the crown surface')
def bezier(points,t):
    return points[0]*(1-t)**3+points[1]*3*(1-t)**2*t+points[2]*3*(1-t)*t*t+points[3]*t**3
for side in [-1,1]:
    curve_points=[Vector((-.010 if side<0 else .001,1.365)),Vector((side*.038,1.345)),Vector((side*.087,1.292)),Vector((side*.137,1.268))]
    vertices=[];faces=[];along=28;across=8
    for i in range(along+1):
        t=i/along;center=bezier(curve_points,t)
        width=.004+.030*math.sin(math.pi*t)**.8
        for j in range(across+1):
            v=j/across;x=-.005+(center.x+.005)*(1-.15*v*t*t)
            bottom=center.y-width*.5;upper=max(center.y+width*.5,1.377-.063*t**1.5)
            z=bottom*(1-v)+upper*v
            x,y=forehead_surface(x,z)
            y-=.0035+.0025*math.sin(math.pi*v)*math.sin(math.pi*t)
            vertices.append((x,y,z))
    for i in range(along):
        for j in range(across):
            a=i*(across+1)+j;f=(a,a+across+1,a+across+2,a+1)
            faces.append(f if side>0 else tuple(reversed(f)))
    data=bpy.data.meshes.new('Parted forehead sweep');data.from_pydata(vertices,[],faces);data.update()
    o=bpy.data.objects.new('Parted forehead sweep',data);collection.objects.link(o)
    attach(o,'Parted forehead fringe '+('left' if side<0 else 'right'),hair,'head')
    solid=o.modifiers.new('Thin sculpted hair volume','SOLIDIFY');solid.thickness=.0015
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    bpy.ops.object.modifier_apply(modifier=solid.name)

for side in [-1,1]:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=10,radius=1,location=(side*.077,-.064,.040))
    o=bpy.context.object;o.scale=(.060,.113,.037)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    attach(o,'Simple flat shoe',shoe)
    verts=[];faces=[];segments=16
    rings=[(.061,.048,.052),(.14,.049,.053),(.28,.053,.056),(.40,.061,.063),(.51,.070,.070),(.59,.077,.075)]
    for z,rx,ry in rings:
        for j in range(segments):
            a=j*math.tau/segments
            verts.append((side*.077+rx*math.cos(a),.015+ry*math.sin(a),z))
    for i in range(len(rings)-1):
        for j in range(segments):
            a=i*segments+j;b=i*segments+(j+1)%segments
            faces.append((a,b,b+segments,a+segments))
    faces.extend([tuple(reversed(range(segments))),tuple((len(rings)-1)*segments+j for j in range(segments))])
    data=bpy.data.meshes.new('Plain trouser leg');data.from_pydata(verts,[],faces);data.update()
    o=bpy.data.objects.new('Plain trouser leg',data);collection.objects.link(o);attach(o,'Plain straight trouser leg',pants)

# Fill the former coat opening with the same fabric, making a single simple top.
data=bpy.data.meshes.new('Plain top front')
data.from_pydata([(-.044,-.112,1.014),(.044,-.112,1.014),(.022,-.157,.870),(0,-.160,.815),(-.022,-.157,.870)],[],[(0,4,3,2,1)])
o=bpy.data.objects.new('Plain top front',data);collection.objects.link(o);attach(o,'Single top front',top)
coat=next(o for o in collection.objects if o.type=='MESH' and 'GEO-spring_jacket' in o.name)
tree=kdtree.KDTree(len(coat.data.vertices))
for v in coat.data.vertices:tree.insert(v.co,v.index)
tree.balance()
data.normals_split_custom_set_from_vertices([coat.data.vertices[tree.find(v.co)[1]].normal for v in data.vertices])
head=next(o for o in collection.objects if o.type=='MESH' and 'GEO-spring_head' in o.name)
neck=[v.co for v in head.data.vertices if v.co.z<1.036]
cx=(min(v.x for v in neck)+max(v.x for v in neck))/2
cy=(min(v.y for v in neck)+max(v.y for v in neck))/2
rx=(max(v.x for v in neck)-min(v.x for v in neck))*.47
ry=(max(v.y for v in neck)-min(v.y for v in neck))*.47
verts=[];faces=[];segments=32
for i in range(segments):
    a=i*math.tau/segments
    verts.extend([(cx+rx*math.cos(a),cy+ry*math.sin(a),1.014),(cx+.076*math.cos(a),-.006+.111*math.sin(a),.994)])
for i in range(segments):
    a=2*i;b=2*((i+1)%segments);faces.append((a,a+1,b+1,b))
data=bpy.data.meshes.new('Fitted plain neckline');data.from_pydata(verts,[],faces);data.update()
o=bpy.data.objects.new('Fitted plain neckline',data);collection.objects.link(o);attach(o,'Single top neckline',top)

# Extend the original short neck through the former shirt collar. Use the original
# painted neck texel so the added join matches the preserved face material.
skin=next(m for m in head.data.materials if m and 'painted face' in m.name)
neck_indices={v.index for v in head.data.vertices if v.co.z<1.036}
sample_uv=next(head.data.uv_layers.active.data[li].uv.copy() for p in head.data.polygons if head.data.materials[p.material_index]==skin for li in p.loop_indices if head.data.loops[li].vertex_index in neck_indices)
verts=[];faces=[];segments=24
for z in [.982,1.038]:
    for j in range(segments):
        a=j*math.tau/segments;verts.append((cx+rx*.985*math.cos(a),cy+ry*.985*math.sin(a),z))
for j in range(segments):
    b=(j+1)%segments;faces.append((j,b,b+segments,j+segments))
data=bpy.data.meshes.new('Neck join');data.from_pydata(verts,[],faces);data.uv_layers.new(name='UVMap')
for loop in data.uv_layers.active.data:loop.uv=sample_uv
o=bpy.data.objects.new('Neck join',data);collection.objects.link(o);attach(o,'Neckline skin join',skin)
rig.name='Spring lightweight web rig'
rig['modifications']='Lightweight variant: plain outfit, flat shoes, parted forehead fringe, no side curls, brown-black irises; slightly larger round glasses'
rig['variant']='lightweight'

meshes=[o for o in collection.objects if o.type=='MESH']
triangles=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes)
scene.camera.location=(1.15,-3.7,1.35)
scene.camera.rotation_euler=(Vector((0,-.02,.74))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
scene.camera.data.ortho_scale=1.65
scene.render.filepath=str(ASSETS/'spring-lite-preview.png')
bpy.ops.object.select_all(action='DESELECT')
for o in [rig,*meshes]:o.select_set(True)
output=ROOT/'public/models/spring-lite.glb'
bpy.ops.export_scene.gltf(filepath=str(output),export_format='GLB',use_selection=True,export_apply=True,export_animations=True,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6,export_extras=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ASSETS/'spring-lite.blend'))
report={'source_sha256':source_hash,'source_unchanged':hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_hash,'triangles':triangles,'mesh_count':len(meshes),'glb_bytes':output.stat().st_size,'parts':report}
(ASSETS/'spring-lite-report.json').write_text(json.dumps(report,indent=2))
bpy.ops.render.render(write_still=True)
scene.camera.location=(0,-3.7,1.35);scene.camera.rotation_euler=(Vector((0,-.025,1.15))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=.72
scene.render.filepath=str(ASSETS/'spring-lite-face.png');bpy.ops.render.render(write_still=True)
print('SPRING_LITE_COMPLETE',json.dumps({k:v for k,v in report.items() if k!='parts'}))
