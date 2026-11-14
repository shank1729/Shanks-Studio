"""Build a detailed, fully 3D character and inspectable portrait renders."""
import bpy,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
from reference_avatar import build_reference_avatar
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
rig,meshes=build_reference_avatar(ROOT)
scene=bpy.context.scene;scene.frame_set(1)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(ROOT/'public/models/reference-character.glb'),export_format='GLB',use_selection=True,export_apply=True,export_animations=True)
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=1000;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.world.use_nodes=True;bg=scene.world.node_tree.nodes['Background'];bg.inputs[0].default_value=(.065,.088,.11,1);bg.inputs[1].default_value=.45
for name,loc,power,color,size in [('Soft key',(-3,3,5),380,(1,.89,.77),4),('Soft fill',(3,3,3),220,(.83,.89,1),4),('Blue rim',(-1,-3,4),220,(.56,.73,1),3)]:
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.color=color;o.data.size=size
    o.rotation_euler=(Vector((-.7,-.7,1.85))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(-.7,3.6,2.0));cam=bpy.context.object;scene.camera=cam
cam.rotation_euler=(Vector((-.7,-.7,1.78))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1.65
scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG'
scene.render.filepath=str(ROOT/'assets/reference-character-front.png')
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.overlay.show_overlays=False
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets/reference-character.blend'))
bpy.ops.render.render(write_still=True)
cam.location=(1.6,3.0,2.0);cam.rotation_euler=(Vector((-.7,-.7,1.78))-cam.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(ROOT/'assets/reference-character-angle.png');bpy.ops.render.render(write_still=True)
print('REFERENCE_CHARACTER_COMPLETE')
