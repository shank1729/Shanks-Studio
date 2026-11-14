"""Build the revised rig, standalone assets, and two neutral-light likeness portraits."""
import bpy,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
from avatar import build_avatar
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
rig,meshes=build_avatar(ROOT)
scene=bpy.context.scene;scene.frame_set(1)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(ROOT/'public/models/shank-character.glb'),export_format='GLB',use_selection=True,export_apply=True,export_animations=True)
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.resolution_x=900;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.world.use_nodes=True;bg=scene.world.node_tree.nodes['Background'];bg.inputs[0].default_value=(.10,.13,.16,1);bg.inputs[1].default_value=.45
for name,loc,power,color,size in [('Portrait key',(-3,3,5),400,(1,.91,.82),4),('Portrait fill',(3,2,3),260,(.87,.91,1),4),('Hair rim',(-1,-3,4),150,(.85,.93,1),3)]:
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.color=color;o.data.size=size
    o.rotation_euler=(Vector((-.7,-.7,1.95))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(-.7,3.4,2.07));cam=bpy.context.object;scene.camera=cam
cam.rotation_euler=(Vector((-.7,-.7,1.96))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO';cam.data.ortho_scale=1.25
scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG'
scene.render.filepath=str(ROOT/'assets/character-likeness-front.png')
for screen in bpy.data.screens:
    for a in screen.areas:
        if a.type=='VIEW_3D':a.spaces.active.region_3d.view_perspective='CAMERA';a.spaces.active.overlay.show_overlays=False
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets/shank-character.blend'))
bpy.ops.render.render(write_still=True)
cam.location=(1.0,3.1,2.11);cam.rotation_euler=(Vector((-.7,-.7,1.96))-cam.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(ROOT/'assets/character-likeness-angle.png')
bpy.ops.render.render(write_still=True)
print('LIKENESS_PREVIEW_COMPLETE')
