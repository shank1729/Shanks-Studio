"""Original, fully modeled and rigged character based on the supplied avatar references.

All visible features are 3D geometry. The only image is a generated textile print.
"""
import bpy, math, random
from mathutils import Vector, Matrix

def build_reference_avatar(root):
    random.seed(19)
    conv=Matrix(((1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)))
    x=-.7;parts=[];mats={}
    def mat(name,rgb,rough=.5,metal=0):
        if name in mats:return mats[name]
        m=bpy.data.materials.new(name);m.use_nodes=True
        p=m.node_tree.nodes.get('Principled BSDF')
        p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
        mats[name]=m;return m
    skin=mat('Warm skin',(.48,.293,.174),.48)
    p=skin.node_tree.nodes.get('Principled BSDF');p.inputs['Subsurface Weight'].default_value=.075;p.inputs['Subsurface Radius'].default_value=(1,.42,.24)
    hair=mat('Soft black hair',(.014,.017,.020),.38);hair.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.29
    hair_high=mat('Hair flow accents',(.023,.026,.028),.42)
    brow=mat('Soft dark brows',(.027,.022,.022),.65)
    lip=mat('Upper rose lip',(.30,.105,.080),.48);lip2=mat('Lower rose lip',(.43,.19,.135),.40)
    cavity=mat('Mouth interior',(.055,.010,.012),.85)
    teeth=mat('Warm enamel',(.82,.78,.65),.28)
    sclera=mat('Warm eye white',(.80,.75,.65),.33)
    iris=mat('Deep brown iris',(.065,.028,.011),.28);pupil=mat('Pupil',(.005,.004,.004),.18)
    gold=mat('Antique gold trim',(.34,.25,.09),.46,.45)
    frames=mat('Fine silver spectacles',(.21,.23,.22),.25,.80)
    cloth=mat('Black botanical textile',(.028,.026,.019),.85)
    pants=mat('Graphite trousers',(.035,.045,.059),.85);shoes=mat('Soft charcoal shoes',(.018,.022,.028),.6)
    skin_shadow=mat('Skin crease',(.31,.16,.09),.66)

    def mesh(name,verts,faces,material,bone='head',uvs=None):
        d=bpy.data.meshes.new(name);d.from_pydata([conv @ Vector(v) for v in verts],[],faces);d.update()
        o=bpy.data.objects.new(name+'__profile',d);bpy.context.collection.objects.link(o);d.materials.append(material)
        for f in d.polygons:f.use_smooth=True
        if uvs:
            d.uv_layers.new(name='UVMap')
            for f in d.polygons:
                for li in f.loop_indices:d.uv_layers.active.data[li].uv=uvs[d.loops[li].vertex_index]
        parts.append((o,bone));return o
    def ell(name,pos,scale,material,bone='head'):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=20)
        o=bpy.context.object;o.name=name+'__profile';o.matrix_world=conv @ Matrix.Translation(Vector(pos)) @ Matrix.Diagonal(Vector((*scale,1)))
        o.data.materials.append(material)
        for f in o.data.polygons:f.use_smooth=True
        parts.append((o,bone));return o
    def strand(name,points,r,material=hair,bone='head'):
        d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.resolution_u=8;d.bevel_resolution=2;d.bevel_depth=r
        s=d.splines.new('BEZIER');s.bezier_points.add(len(points)-1)
        for b,co in zip(s.bezier_points,points):b.co=conv @ Vector(co);b.handle_left_type='AUTO';b.handle_right_type='AUTO'
        o=bpy.data.objects.new(name+'__profile',d);bpy.context.collection.objects.link(o);d.materials.append(material)
        bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
        o=bpy.context.object;parts.append((o,bone));return o
    def limb(name,a,b,r,material,bone):
        v=Vector(b)-Vector(a);mid=(Vector(a)+Vector(b))/2
        o=ell(name,mid,(r,r,v.length/2+r*.25),material,bone)
        o.matrix_world=conv @ Matrix.Translation(mid) @ v.to_track_quat('Z','Y').to_matrix().to_4x4() @ Matrix.Diagonal(Vector((r,r,v.length/2+r*.25,1)))
        return o

    # Generate a small original floral textile, using painted petal shapes in UV space.
    n=512;pixels=[0.0]*(n*n*4)
    palette=[(.62,.35,.12),(.51,.17,.10),(.38,.42,.22),(.69,.51,.23)]
    flowers=[]
    for row in range(5):
        for col in range(5):
            cx=(col+.5+(row%2)*.32)/5;cy=(row+.5)/5
            flowers.append((cx%1,cy,.060+random.random()*.012,random.random()*math.tau))
    for iy in range(n):
        for ix in range(n):
            u=ix/n;v=iy/n;c=(.038,.036,.028)
            for fx,fy,rad,rot in flowers:
                dx=(u-fx+.5)%1-.5;dy=(v-fy+.5)%1-.5
                if abs(dx)>rad*1.2 or abs(dy)>rad*1.2:continue
                rr=math.hypot(dx,dy);a=math.atan2(dy,dx)-rot
                k=round(a/(math.tau/9));theta=a-k*math.tau/9
                along=rr*math.cos(theta);across=rr*math.sin(theta)
                if ((along-rad*.58)/(rad*.35))**2+(across/(rad*.095))**2<1:c=palette[k%4]
                if rr<rad*.12:c=palette[2]
            i=(iy*n+ix)*4;pixels[i:i+4]=[*c,1]
    textile=bpy.data.images.new('Original botanical print',width=n,height=n);textile.pixels.foreach_set(pixels)
    textile.filepath_raw=str(root/'assets/reference-botanical-print.png');textile.file_format='PNG';textile.save();textile.pack()
    tex=cloth.node_tree.nodes.new('ShaderNodeTexImage');tex.image=textile
    cloth.node_tree.links.new(tex.outputs['Color'],cloth.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])

    # Neck/chest and square-neck tailored bodice, including a contrasting neckline binding.
    ell('Neck',(x,1.545,.735),(.107,.18,.110),skin)
    ell('Upper chest',(x,1.365,.754),(.252,.175,.184),skin,'spine')
    verts=[];fs=[];uv=[];nr=24;nc=80
    for i in range(nr+1):
        t=i/nr
        for j in range(nc+1):
            a=j*math.tau/nc;front=math.cos(a)
            top=1.435 if front<0 else 1.282+.143*abs(math.sin(a))**7
            y=.83+(top-.83)*t;w=.235+.030*math.sin(t*math.pi*.75);d=.190+.018*math.sin(t*math.pi)
            verts.append((x+w*math.sin(a),y,.79-d*math.cos(a)));uv.append((j/nc*2,t*1.25))
    for i in range(nr):
        for j in range(nc):a=i*(nc+1)+j;fs.append((a,a+nc+1,a+nc+2,a+1))
    mesh('Square neck patterned bodice',verts,fs,cloth,'spine',uv)
    neckline=[verts[nr*(nc+1)+j] for j in range(nc+1)]
    strand('Neckline binding',neckline,.008,gold,'spine')
    strand('Waist seam',[(x+.237*math.sin(a),.91,.79-.195*math.cos(a)) for a in [j*math.tau/64 for j in range(65)]],.005,gold,'pelvis')
    ell('Seated hips',(x,.82,.86),(.265,.20,.24),pants,'pelvis')

    for side in [-1,1]:
        suffix='L' if side<0 else 'R';arm='upper_arm.'+suffix;fore='forearm.'+suffix
        shoulder=(x+side*.26,1.38,.77);elbow=(x+side*.40,1.12,.47);wrist=(x+side*.31,1.08,.13)
        limb('Upper arm '+suffix,shoulder,elbow,.090,skin,arm)
        puff=ell('Patterned puff sleeve '+suffix,(x+side*.316,1.322,.68),(.157,.17,.158),cloth,arm)
        # Gentle gathered folds rather than a smooth spherical sleeve.
        for v in puff.data.vertices:
            a=math.atan2(v.co.x,v.co.z);f=1+.038*math.cos(a*10)*max(0,1-v.co.y*v.co.y)
            v.co.x*=f;v.co.z*=f
        axis=(Vector(elbow)-Vector(shoulder)).normalized();cuffcenter=Vector(shoulder).lerp(Vector(elbow),.65)
        cu=axis.cross(Vector((0,1,0))).normalized();cv=axis.cross(cu).normalized()
        for shift in [-.012,.012]:
            strand('Fine sleeve binding '+suffix,[cuffcenter+axis*shift+.100*(cu*math.cos(a)+cv*math.sin(a)) for a in [j*math.tau/48 for j in range(49)]],.0028,gold,arm)
        limb('Forearm '+suffix,elbow,wrist,.070,skin,fore)
        palm=(x+side*.30,1.079,.073)
        ell('Palm '+suffix,palm,(.067,.034,.090),skin,fore)
        # Four individually modeled fingers with joints and small fingernails.
        for j in range(4):
            fx=palm[0]+(j-1.5)*.029;fy=1.079;startz=.035;length=[.091,.110,.104,.078][j]
            a=(fx,fy,startz);b=(fx,fy-.012,startz-length*.52);c=(fx,fy-.022,startz-length)
            limb('Finger proximal '+suffix+str(j),a,b,.015,skin,fore);limb('Finger distal '+suffix+str(j),b,c,.013,skin,fore)
            ell('Fingernail '+suffix+str(j),(fx,fy-.012,startz-length+.012),(.008,.004,.014),lip2,fore)
        limb('Thumb base '+suffix,(palm[0]-side*.052,1.075,.09),(palm[0]-side*.088,1.079,.04),.023,skin,fore)
        limb('Thumb tip '+suffix,(palm[0]-side*.088,1.079,.04),(palm[0]-side*.080,1.076,-.001),.019,skin,fore)
        hip=(x+side*.15,.8,.83);knee=(x+side*.18,.63,.38);ankle=(x+side*.19,.17,.38)
        limb('Thigh '+suffix,hip,knee,.113,pants,'thigh.'+suffix);limb('Shin '+suffix,knee,ankle,.092,pants,'shin.'+suffix)
        ell('Flat shoe '+suffix,(x+side*.19,.11,.26),(.116,.085,.212),shoes,'shin.'+suffix)
        ell('Shoe sole '+suffix,(x+side*.19,.060,.26),(.120,.025,.214),gold,'shin.'+suffix)

    # Head: smooth cheek/chin profile, sculpted nasal bridge and rounded tip.
    profile=[(1.615,.026,.050,.72),(1.65,.110,.125,.71),(1.71,.182,.182,.705),
             (1.79,.237,.220,.705),(1.88,.272,.244,.705),(1.98,.280,.249,.710),
             (2.09,.268,.246,.718),(2.19,.239,.225,.727),(2.28,.165,.162,.737),
             (2.34,.065,.069,.742),(2.35,.004,.004,.744)]
    def interp(y):
        k=next((k for k in range(len(profile)-1) if profile[k][0]<=y<=profile[k+1][0]),len(profile)-2)
        t=(y-profile[k][0])/(profile[k+1][0]-profile[k][0]);vals=[]
        for j in range(1,4):
            a,b,c,d=profile[max(0,k-1)][j],profile[k][j],profile[k+1][j],profile[min(len(profile)-1,k+2)][j]
            vals.append(.5*(2*b+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
        return vals
    def g(dx,dy,sx,sy):return math.exp(-.5*((dx/sx)**2+(dy/sy)**2))
    def relief(dx,y):
        return .042*g(dx,y-1.995,.029,.076)+.094*g(dx,y-1.90,.033,.031)+.024*g(abs(dx)-.041,y-1.882,.021,.023)+.023*g(abs(dx)-.155,y-1.862,.066,.058)-.010*g(abs(dx)-.124,y-2.005,.062,.037)
    verts=[];fs=[];nr=120;nc=160
    for i in range(nr+1):
        y=1.615+.735*i/nr;w,d,cz=interp(y)
        for j in range(nc):
            a=j*math.tau/nc;dx=w*math.sin(a);f=math.cos(a);z=cz-d*f
            if f>0:z-=relief(dx,y)*f**4
            verts.append((x+dx,y,z))
    for i in range(nr):
        for j in range(nc):
            a=i*nc+j;b=i*nc+(j+1)%nc;ids=(a,a+nc,b+nc,b)
            center=sum((Vector(verts[v]) for v in ids),Vector())/4
            fs.append(ids)
    fs.extend([tuple(range(nc)),tuple(reversed([nr*nc+j for j in range(nc)]))])
    mesh('Sculpted smiling face',verts,fs,skin)
    # Smile cavity, curved enamel row, tongue and sculpted lips have actual depth.
    vs=[];fs=[]
    for i in range(65):
        u=-1+2*i/64;fade=max(0,1-u*u)**.65
        vs.extend([(x+.123*u,1.799+.003*fade,.444+.065*u*u),(x+.123*u,1.799-.025*fade,.444+.065*u*u)])
    for i in range(64):a=i*2;fs.append((a,a+2,a+3,a+1))
    mesh('Recessed smile interior',vs,fs,cavity)
    vs=[];fs=[]
    for i in range(41):
        u=-1+2*i/40
        vs.extend([(x+.097*u,1.798-.003*u*u,.439+.046*u*u),(x+.097*u,1.783+.009*u*u,.439+.046*u*u)])
    for i in range(40):a=i*2;fs.append((a,a+2,a+3,a+1))
    mesh('Continuous curved enamel smile',vs,fs,teeth)
    for upper in [True,False]:
        vs=[];fs=[]
        for i in range(65):
            u=-1+2*i/64;fade=max(0,1-u*u)**.65;dx=.123*u
            inner=1.799+(.003*fade if upper else -.025*fade)
            outer=inner+(.010*fade if upper else -.012*fade)
            for j in range(5):
                t=j/4;y=inner*(1-t)+outer*t;z=.440+.065*u*u-.012*math.sin(t*math.pi)*fade
                vs.append((x+dx,y,z))
        for i in range(64):
            for j in range(4):a=i*5+j;fs.append((a,a+1,a+6,a+5) if upper else (a,a+5,a+6,a+1))
        mesh('Sculpted upper smile lip' if upper else 'Sculpted lower smile lip',vs,fs,lip if upper else lip2)
    for side in [-1,1]:
        cx=x+side*.121;cy=2.006
        vs=[(cx,cy,.460)];n=64
        for j in range(n):
            a=j*math.tau/n;dx=.069*math.cos(a);dy=(.031 if math.sin(a)>0 else .024)*math.sin(a)
            vs.append((cx+dx,cy+dy+side*dx*.10,.466))
        mesh('Almond eye',vs,[(0,1+(j+1)%n,1+j) for j in range(n)],sclera)
        ell('Brown iris',(cx,cy,.459),(.026,.027,.006),iris);ell('Pupil',(cx,cy,.451),(.012,.014,.002),pupil)
        ell('Eye highlight',(cx-.008,cy+.009,.448),(.004,.004,.001),teeth)
        up=[(cx+.069*math.cos(a),cy+.031*math.sin(a)+side*.069*math.cos(a)*.10,.464) for a in [j*math.pi/20 for j in range(21)]]
        lo=[(cx+.069*math.cos(a),cy+.024*math.sin(a)+side*.069*math.cos(a)*.10,.465) for a in [math.pi+j*math.pi/20 for j in range(21)]]
        strand('Upper sculpted eyelid',up,.0045,skin);strand('Fine eyelashes',[(a,b-.001,c-.003) for a,b,c in up],.0014,brow)
        strand('Lower sculpted eyelid',lo,.0033,skin)
        # A tapered eyebrow ribbon, not a constant-thickness tube.
        vs=[];fs=[]
        for j in range(25):
            t=j/24;dx=.045+.165*t;y=2.093+.025*math.sin(t*math.pi)-.007*t;z=.464+.06*t*t
            thickness=.014*math.sin(math.pi*(.16+.82*t))
            vs.extend([(x+side*dx,y-thickness*.3,z),(x+side*dx,y+thickness*.7,z-.001)])
        for j in range(24):a=j*2;fs.append((a,a+1,a+3,a+2) if side>0 else (a+2,a+3,a+1,a))
        mesh('Tapered expressive eyebrow',vs,fs,brow)
        ell('Ear',(x+side*.281,1.969,.724),(.034,.067,.037),skin)
        ell('Ear inner fold',(x+side*.301,1.970,.697),(.011,.035,.010),skin_shadow)
        ell('Small crystal stud',(x+side*.298,1.916,.685),(.010,.010,.009),frames)
        # Thin oval silver glasses, matching the reference's unobtrusive frames.
        pts=[]
        for j in range(49):
            a=j*math.tau/48;dx=side*(.126+.106*math.cos(a));y=2.009+.056*math.sin(a)
            pts.append((x+dx,y,.411+.058*(abs(dx)/.24)**2))
        strand('Fine oval spectacle rim',pts,.0023,frames)
        strand('Spectacle temple',[(x+side*.230,2.024,.465),(x+side*.287,2.030,.603),(x+side*.303,2.020,.746)],.0021,frames)
    strand('Fine spectacle bridge',[(x-.020,2.025,.413),(x,2.039,.404),(x+.020,2.025,.413)],.0021,frames)

    # Asymmetric sculpted hair cap with a gently off-center part.
    vs=[];fs=[];nr=40;nc=112
    for i in range(nr+1):
        for j in range(nc):
            a=j*math.tau/nc;f=math.cos(a);limit=.82+.50*(1-f)+.055*math.sin(a)
            phi=.008+(limit-.008)*i/nr
            vs.append((x+.300*math.sin(phi)*math.sin(a),1.997+.397*math.cos(phi),.742-.270*math.sin(phi)*math.cos(a)))
    for i in range(nr):
        for j in range(nc):a=i*nc+j;b=i*nc+(j+1)%nc;fs.append((a,b,b+nc,a+nc))
    mesh('Fitted hair crown',vs,fs,hair)
    # Sweeping locks are closed, varying-section meshes, not image planes or cylinders.
    def lock(name,path,widths,depths):
        vs=[];fs=[];nc=24
        for i,p in enumerate(path):
            for j in range(nc):
                a=j*math.tau/nc;groove=1+.025*math.cos(a*7)
                vs.append((p[0]+widths[i]*math.cos(a)*groove,p[1],p[2]+depths[i]*math.sin(a)*groove))
        for i in range(len(path)-1):
            for j in range(nc):a=i*nc+j;b=i*nc+(j+1)%nc;fs.append((a,b,b+nc,a+nc))
        fs.extend([tuple(reversed(range(nc))),tuple((len(path)-1)*nc+j for j in range(nc))])
        o=mesh(name,vs,fs,hair);sub=o.modifiers.new('Flowing sculpted volume','SUBSURF');sub.levels=2;sub.render_levels=2
        return o
    # Rear silhouette and layered waves, slightly fuller over the left shoulder.
    for side in [-1,1]:
        for layer in range(4):
            u=layer/3
            path=[(x+side*(.14+.020*u),2.30,.78+.05*u),
                  (x+side*(.29+.025*u),2.08,.78+.15*u),
                  (x+side*(.33+.015*u),1.88,.80+.18*u),
                  (x+side*(.36+.04*u),1.65,.80+.17*u),
                  (x+side*(.30+.03*u),1.43,.85+.17*u),
                  (x+side*(.29+.04*u),1.17,.77+.15*u),
                  (x+side*(.28+.02*u),1.08,.81+.13*u)]
            lock('Layered back hair '+str(side)+str(layer),path,[.040,.075,.090,.090,.085,.055,.002],[.040,.070,.075,.075,.065,.045,.002])
    left=[(x+.035,2.375,.660),(x-.12,2.30,.555),(x-.24,2.17,.514),(x-.31,2.04,.474),
          (x-.38,1.88,.490),(x-.33,1.74,.515),(x-.39,1.57,.476),(x-.31,1.40,.493),(x-.35,1.25,.562),(x-.29,1.12,.61)]
    lock('Long sweeping front wave',left,[.045,.067,.074,.080,.072,.064,.072,.058,.045,.001],[.040,.035,.045,.047,.046,.040,.041,.034,.025,.001])
    right=[(x+.040,2.375,.660),(x+.17,2.29,.565),(x+.25,2.18,.550),(x+.32,2.03,.578),
           (x+.33,1.82,.615),(x+.31,1.59,.635),(x+.35,1.39,.654),(x+.30,1.19,.700)]
    lock('Soft right face framing wave',right,[.040,.043,.054,.056,.048,.052,.037,.001],[.035,.030,.033,.034,.031,.032,.025,.001])
    for side,path in [(-1,left),(1,right)]:
        for k in range(3):
            pts=[(p[0]+(k-1)*.018,p[1],p[2]-.035) for p in path[1:-1]]
            strand('Subtle wave flow',pts,.0007,hair_high)

    # Whole-body bone hierarchy, with weighted meshes and a looped welcome idle.
    bones=[('root',(x,0,.9),(x,.35,.9),None),('pelvis',(x,.75,.86),(x,1,.8),'root'),('spine',(x,1,.8),(x,1.5,.72),'pelvis'),('head',(x,1.5,.72),(x,2.17,.7),'spine')]
    for side in [-1,1]:
        suffix='L' if side<0 else 'R'
        bones.extend([('upper_arm.'+suffix,(x+side*.26,1.38,.77),(x+side*.40,1.12,.47),'spine'),('forearm.'+suffix,(x+side*.40,1.12,.47),(x+side*.31,1.08,.13),'upper_arm.'+suffix),('thigh.'+suffix,(x+side*.15,.8,.83),(x+side*.18,.63,.38),'pelvis'),('shin.'+suffix,(x+side*.18,.63,.38),(x+side*.19,.17,.38),'thigh.'+suffix)])
    data=bpy.data.armatures.new('Reference character skeleton');rig=bpy.data.objects.new('Reference character rig',data);bpy.context.collection.objects.link(rig)
    bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
    for name,a,b,parent in bones:
        q=data.edit_bones.new(name);q.head=conv @ Vector(a);q.tail=conv @ Vector(b)
        if parent:q.parent=data.edit_bones[parent]
    bpy.ops.object.mode_set(mode='OBJECT')
    # Apply subdivision before binding to preserve the detailed exported hair volumes.
    for o,b in parts:
        bpy.context.view_layer.objects.active=o
        for mod in list(o.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
        mw=o.matrix_world.copy();o.parent=rig;o.matrix_world=mw
        vg=o.vertex_groups.new(name=b);vg.add(list(range(len(o.data.vertices))),1,'REPLACE')
        mod=o.modifiers.new('Character skin','ARMATURE');mod.object=rig
    scene=bpy.context.scene;scene.frame_start=1;scene.frame_end=121;scene.render.fps=30
    for frame in range(1,122,4):
        t=(frame-1)/120*math.tau
        for name in ['spine','head','forearm.R']:
            q=rig.pose.bones[name];q.rotation_mode='XYZ'
            if name=='spine':q.rotation_euler=(.010*math.sin(t),0,0)
            elif name=='head':q.rotation_euler=(.015*math.sin(t),.028*math.sin(t),.010*math.sin(t))
            else:q.rotation_euler=(.020*math.sin(t),0,0)
            q.keyframe_insert('rotation_euler',frame=frame,group=name)
    rig.animation_data.action.name='Warm welcome idle';scene.frame_set(1)
    return rig,[o for o,b in parts]
