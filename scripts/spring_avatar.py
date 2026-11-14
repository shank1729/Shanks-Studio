"""Append the customized, original Spring meshes and lightweight web rig."""
import bpy,json
from mathutils import Vector

def build_spring_avatar(root):
    config=json.loads((root/'scripts/avatar-config.json').read_text())
    filename='spring-lite.blend' if config.get('style')=='spring-lite' else 'spring-professional.blend'
    path=root/'assets'/filename
    if not path.exists():raise FileNotFoundError('Build the Spring customization before rebuilding the house.')
    with bpy.data.libraries.load(str(path),link=False) as (source,target):
        target.collections=['SPRING-WEB']
    collection=target.collections[0]
    bpy.context.scene.collection.children.link(collection)
    rig=next(o for o in collection.all_objects if o.type=='ARMATURE')
    meshes=[o for o in collection.all_objects if o.type=='MESH']
    bpy.context.view_layer.update()
    points=[o.matrix_world @ Vector(v) for o in meshes for v in o.bound_box]
    low=min(p.z for p in points);high=max(p.z for p in points)
    factor=2.45/(high-low)
    rig.scale=(factor,)*3;rig.location.z=-low*factor
    return rig,meshes
