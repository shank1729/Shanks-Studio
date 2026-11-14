"""Read the official Spring source without enabling embedded Python scripts."""
import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent.parent
result={'file':bpy.data.filepath,'scenes':[s.name for s in bpy.data.scenes],
        'collections':[c.name for c in bpy.data.collections],
        'objects':[],'materials':[],'images':[],'rigs':[]}
for o in bpy.data.objects:
    record={'name':o.name,'type':o.type,'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'location':list(o.location),'dimensions':list(o.dimensions),'parent':o.parent.name if o.parent else None}
    if o.type=='MESH':
        record.update(vertices=len(o.data.vertices),polygons=len(o.data.polygons),materials=[m.name if m else None for m in o.data.materials],modifiers=[{'type':m.type,'name':m.name,'enabled':m.show_viewport} for m in o.modifiers],shape_keys=list(o.data.shape_keys.key_blocks.keys()) if o.data.shape_keys else [],bounds=[list(o.matrix_world @ Vector(v)) for v in o.bound_box])
    result['objects'].append(record)
    if o.type=='ARMATURE':result['rigs'].append({'name':o.name,'bones':len(o.data.bones),'bone_names':[b.name for b in o.data.bones],'properties':list(o.keys())})
for m in bpy.data.materials:
    result['materials'].append({'name':m.name,'nodes':[{'name':n.name,'type':n.type} for n in m.node_tree.nodes] if m.use_nodes else [],'color':list(m.diffuse_color)})
for i in bpy.data.images:result['images'].append({'name':i.name,'filepath':i.filepath,'size':list(i.size),'packed':bool(i.packed_file)})
(ROOT/'assets/spring-source/inspection.json').write_text(json.dumps(result,indent=2))
print('SPRING_INSPECTION_COMPLETE',len(result['objects']),'objects',len(result['images']),'images')
