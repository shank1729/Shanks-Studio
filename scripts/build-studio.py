"""Run: blender --background --python scripts/build-studio.py
Creates an editable .blend and the GLB consumed by the website.
"""
import bpy, json, math, sys
from pathlib import Path
from mathutils import Matrix

root = Path(__file__).resolve().parent.parent
sys.path.insert(0,str(root/'scripts'))
from avatar import build_avatar
shapes = json.loads((root / 'scripts/studio-blueprint.json').read_text())
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
# Three.js uses Y-up; Blender uses Z-up.
conversion = Matrix(((1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)))
for shape in shapes:
    p=shape['parameters']
    if shape['type']=='BoxGeometry':
        bpy.ops.mesh.primitive_cube_add(size=1)
        obj=bpy.context.object
        for vertex in obj.data.vertices:
            vertex.co.x *= p['width']
            vertex.co.y *= p['height']
            vertex.co.z *= p['depth']
        bevel=obj.modifiers.new('Soft crafted edges','BEVEL');bevel.width=.025;bevel.segments=3
        obj.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
    elif shape['type']=='SphereGeometry':
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=20,radius=p['radius'])
        obj=bpy.context.object
        for face in obj.data.polygons: face.use_smooth=True
    elif shape['type']=='TorusGeometry':
        bpy.ops.mesh.primitive_torus_add(major_radius=p['radius'],minor_radius=p['tube'],major_segments=64,minor_segments=12)
        obj=bpy.context.object
        # Three.js torus lies in XY too.
        for face in obj.data.polygons: face.use_smooth=True
    else: continue
    values=shape['matrix']
    transform=Matrix(tuple(tuple(values[col*4+row] for col in range(4)) for row in range(4)))
    obj.matrix_world=conversion @ transform
    obj.name=shape['name']
    mat=bpy.data.materials.new(shape['name']+' material');mat.use_nodes=True
    shader=mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value=(*shape['color'],1)
    shader.inputs['Roughness'].default_value=.48
    shader.inputs['Metallic'].default_value=.12
    if 'Emission Color' in shader.inputs:
        shader.inputs['Emission Color'].default_value=(*shape['emission'],1)
        shader.inputs['Emission Strength'].default_value=shape['emissionStrength']
    obj.data.materials.append(mat)

# Align the chair with the laptop, then add the original animated character.
for obj in list(bpy.context.scene.objects):
    if obj.name.startswith('Seat'):obj.location.x-=.7
rig,avatar_meshes=build_avatar(root)

for name, location, energy, color, size in [
    ('Warm softbox',(-3,-5,7),1000,(1,.83,.66),5),
    ('Lavender window',(3,2,4),700,(.54,.46,1),4),
    ('Cool fill',(-4,3,3),450,(.56,.75,1),3)]:
    bpy.ops.object.light_add(type='AREA',location=location)
    light=bpy.context.object;light.name=name;light.data.energy=energy;light.data.color=color;light.data.shape='DISK';light.data.size=size
    light.rotation_euler=((Matrix.Translation((0,0,1)).translation-light.location).to_track_quat('-Z','Y').to_euler())
bpy.ops.object.camera_add(location=(9,-11,7.5))
camera=bpy.context.object;camera.rotation_euler=(Matrix.Translation((0,0,1)).translation-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=10
bpy.context.scene.camera=camera
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32
scene.render.resolution_x=1400;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.world.color=(.08,.1,.16)
(root/'assets').mkdir(exist_ok=True);(root/'public/models').mkdir(parents=True,exist_ok=True)
portrait=bpy.data.scenes.new('Character portrait')
for obj in [rig,*avatar_meshes,*[o for o in scene.objects if o.type=='LIGHT']]:portrait.collection.objects.link(obj)
camera_data=bpy.data.cameras.new('Portrait camera');portrait_camera=bpy.data.objects.new('Portrait camera',camera_data);portrait.collection.objects.link(portrait_camera)
portrait_camera.location=(2.3,5.8,2.8);portrait_camera.rotation_euler=(Matrix.Translation((-.7,-.65,1.25)).translation-portrait_camera.location).to_track_quat('-Z','Y').to_euler()
camera_data.type='ORTHO';camera_data.ortho_scale=3;portrait.camera=portrait_camera
portrait.world=bpy.data.worlds.new('Portrait background');portrait.world.use_nodes=True;portrait.world.node_tree.nodes['Background'].inputs[0].default_value=(.1,.13,.18,1)
portrait.render.engine='CYCLES';portrait.cycles.samples=24;portrait.render.resolution_x=850;portrait.render.resolution_y=950;portrait.render.resolution_percentage=100
portrait.render.image_settings.file_format='PNG';portrait.render.filepath=str(root/'assets/character-preview.png');portrait.frame_start=1;portrait.frame_end=121
bpy.ops.object.select_all(action='DESELECT')
for obj in [rig,*avatar_meshes]:obj.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.gltf(filepath=str(root/'public/models/shank-character.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_lights=False,export_cameras=False,export_animations=True)
bpy.ops.wm.save_as_mainfile(filepath=str(root/'assets/floating-studio.blend'))
bpy.ops.export_scene.gltf(filepath=str(root/'public/models/floating-studio.glb'),export_format='GLB',use_active_scene=True,export_lights=False,export_cameras=False,export_animations=True)
bpy.ops.render.render(scene=portrait.name,write_still=True)
bpy.context.window.scene=portrait
bpy.data.scenes.remove(scene)
bpy.ops.wm.save_as_mainfile(filepath=str(root/'assets/shank-character.blend'))
print('Saved editable Blender scene and browser GLB.')
