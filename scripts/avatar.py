"""Personal rigged character with a continuous face refined from portrait references."""
import bpy, math, json
from mathutils import Vector, Matrix

def build_avatar(root):
    config=json.loads((root/'scripts/avatar-config.json').read_text())
    if config.get('style') in {'spring-professional','spring-lite'}:
        from spring_avatar import build_spring_avatar
        return build_spring_avatar(root)
    if config.get('style')=='reference-character':
        from reference_avatar import build_reference_avatar
        return build_reference_avatar(root)
    conversion=Matrix(((1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)))
    def point(v): return conversion @ Vector(v)
    meshes=[];materials={}
    def material(hex_color):
        if hex_color in materials:return materials[hex_color]
        rgb=[int(hex_color[i:i+2],16)/255 for i in (1,3,5)]
        rgb=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
        mat=bpy.data.materials.new('Avatar '+hex_color);mat.use_nodes=True
        shader=mat.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=(*rgb,1);shader.inputs['Roughness'].default_value=.7
        materials[hex_color]=mat;return mat
    def ellipsoid(name,pos,scale,color,bone):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=24,radius=1)
        obj=bpy.context.object;obj.name='Avatar '+name+'__profile'
        obj.matrix_world=conversion @ Matrix.Translation(Vector(pos)) @ Matrix.Diagonal(Vector((*scale,1)))
        obj.data.materials.append(material(color))
        for poly in obj.data.polygons:poly.use_smooth=True
        meshes.append((obj,bone));return obj
    def limb(name,a,b,r,color,bone):
        midpoint=(Vector(a)+Vector(b))/2
        obj=ellipsoid(name,midpoint,(r,r,(Vector(b)-Vector(a)).length/2+r*.3),color,bone)
        direction=Vector(b)-Vector(a)
        obj.matrix_world=conversion @ Matrix.Translation(midpoint) @ direction.to_track_quat('Z','Y').to_matrix().to_4x4() @ Matrix.Diagonal(Vector((r,r,direction.length/2+r*.3,1)))
        return obj
    def curve(name,points,color,bone,r=.012):
        data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.bevel_depth=r
        data.bevel_resolution=1 if r<.003 else 2;data.resolution_u=6 if r<.003 else 12
        spline=data.splines.new('BEZIER');spline.bezier_points.add(len(points)-1)
        for vertex,position in zip(spline.bezier_points,points):vertex.co=point(position);vertex.handle_left_type='AUTO';vertex.handle_right_type='AUTO'
        obj=bpy.data.objects.new('Avatar '+name+'__profile',data);bpy.context.collection.objects.link(obj);obj.data.materials.append(material(color))
        bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj;bpy.ops.object.convert(target='MESH');obj=bpy.context.object
        meshes.append((obj,bone));return obj
    skin=config['skin'];hair=config['hair'];shirt=config['shirt'];pants=config['pants'];shoe=config['shoes'];x=-.7
    ellipsoid('hips',(x,.82,.86),(.29,.22,.27),pants,'pelvis')
    ellipsoid('hoodie torso',(x,1.17,.79),(.32,.4,.25),shirt,'spine')
    ellipsoid('hood',(x,1.47,.9),(.3,.18,.2),shirt,'spine')
    ellipsoid('neck',(x,1.53,.72),(.105,.17,.105),skin,'head')
    from likeness import build_likeness_face
    build_likeness_face(config,x,ellipsoid,curve,material,conversion,meshes)
    for side in (-1,1):
        suffix='L' if side<0 else 'R'
        shoulder=(x+side*.26,1.38,.77);elbow=(x+side*.4,1.12,.47);wrist=(x+side*.32,1.1,-.07)
        limb('sleeve '+suffix,shoulder,elbow,.125,shirt,'upper_arm.'+suffix)
        limb('forearm '+suffix,elbow,wrist,.087,skin,'forearm.'+suffix)
        ellipsoid('hand '+suffix,(x+side*.32,1.1,-.14),(.09,.055,.13),skin,'forearm.'+suffix)
        hip=(x+side*.17,.8,.83);knee=(x+side*.19,.63,.38);ankle=(x+side*.2,.17,.38)
        limb('thigh '+suffix,hip,knee,.13,pants,'thigh.'+suffix)
        limb('shin '+suffix,knee,ankle,.11,pants,'shin.'+suffix)
        ellipsoid('sneaker '+suffix,(x+side*.2,.115,.25),(.14,.11,.24),shoe,'shin.'+suffix)
        ellipsoid('sneaker sole '+suffix,(x+side*.2,.065,.25),(.145,.035,.245),'#e4e5e1','shin.'+suffix)
    if config.get('beard'):
        ellipsoid('beard',(x,1.69,.49),(.25,.14,.2),hair,'head')
    for side in (-1,1):limb('hoodie drawstring',(x+side*.075,1.44,.55),(x+side*.09,1.2,.53),.012,'#d7dacd','spine')
    bones=[('root',(x,0,.9),(x,.35,.9),None),('pelvis',(x,.75,.86),(x,1,.8),'root'),('spine',(x,1,.8),(x,1.5,.72),'pelvis'),('head',(x,1.5,.72),(x,2.16,.7),'spine')]
    for side in (-1,1):
        suffix='L' if side<0 else 'R'
        bones.extend([
            ('upper_arm.'+suffix,(x+side*.26,1.38,.77),(x+side*.4,1.12,.47),'spine'),
            ('forearm.'+suffix,(x+side*.4,1.12,.47),(x+side*.32,1.1,-.07),'upper_arm.'+suffix),
            ('thigh.'+suffix,(x+side*.17,.8,.83),(x+side*.19,.63,.38),'pelvis'),
            ('shin.'+suffix,(x+side*.19,.63,.38),(x+side*.2,.17,.38),'thigh.'+suffix)])
    data=bpy.data.armatures.new('Developer character rig');rig=bpy.data.objects.new('Shank character rig',data);bpy.context.collection.objects.link(rig)
    bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
    for name,a,b,parent in bones:
        bone=data.edit_bones.new(name);bone.head=point(a);bone.tail=point(b)
        if parent:bone.parent=data.edit_bones[parent]
    bpy.ops.object.mode_set(mode='OBJECT')
    for obj,bone in meshes:
        matrix=obj.matrix_world.copy();obj.parent=rig;obj.matrix_world=matrix
        group=obj.vertex_groups.new(name=bone);group.add(list(range(len(obj.data.vertices))),1,'REPLACE')
        modifier=obj.modifiers.new('Character pose','ARMATURE');modifier.object=rig
    # One continuous idle loop, with breathing, head motion and alternating typing.
    scene=bpy.context.scene;scene.frame_start=1;scene.frame_end=121;scene.render.fps=30
    for frame in range(1,122,4):
        phase=(frame-1)/120*math.tau
        for name in ('spine','head','forearm.L','forearm.R'):
            bone=rig.pose.bones[name];bone.rotation_mode='XYZ'
            if name=='spine':bone.rotation_euler=(.012*math.sin(phase),0,0)
            elif name=='head':bone.rotation_euler=(.02*math.sin(phase),.04*math.sin(phase),0)
            else:bone.rotation_euler=(.05*math.sin(phase*6+(0 if name.endswith('L') else math.pi)),0,0)
            bone.keyframe_insert(data_path='rotation_euler',frame=frame,group=name)
    rig.animation_data.action.name='Studio idle and typing'
    scene.frame_set(1)
    return rig,[obj for obj,_ in meshes]
