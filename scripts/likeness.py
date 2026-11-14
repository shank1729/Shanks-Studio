"""Original web-friendly face geometry refined from the user's four portrait references.

No photographs are embedded in the model. Coordinates follow avatar.py's Y-up space.
"""
import bpy, math
from mathutils import Vector

def build_likeness_face(config, x, ellipsoid, curve, material, conversion, meshes):
    skin=config['skin'];hair=config['hair'];bone='head'
    def mesh(name,vertices,faces,color):
        data=bpy.data.meshes.new(name);data.from_pydata([conversion @ Vector(v) for v in vertices],[],faces);data.update()
        o=bpy.data.objects.new('Avatar '+name+'__profile',data);bpy.context.collection.objects.link(o)
        o.data.materials.append(material(color))
        for p in o.data.polygons:p.use_smooth=True
        meshes.append((o,bone));return o
    def gauss(a,b,sa,sb):return math.exp(-.5*((a/sa)**2+(b/sb)**2))
    # Continuous skin surface: cheeks, jaw, chin, nose and eye sockets share one mesh.
    profile=[(1.59,.035,.065,.705),(1.625,.105,.115,.705),(1.68,.178,.170,.70),
             (1.76,.224,.210,.70),(1.85,.270,.242,.70),(1.96,.294,.251,.70),
             (2.07,.284,.250,.705),(2.18,.250,.225,.715),(2.26,.195,.180,.725),
             (2.32,.105,.102,.735),(2.345,.008,.008,.74)]
    def interpolate(y):
        k=next((i for i in range(len(profile)-1) if profile[i][0]<=y<=profile[i+1][0]),len(profile)-2)
        t=(y-profile[k][0])/(profile[k+1][0]-profile[k][0]);t=max(0,min(1,t));vals=[]
        for j in range(1,4):
            a=profile[max(0,k-1)][j];b=profile[k][j];c=profile[k+1][j];d=profile[min(len(profile)-1,k+2)][j]
            vals.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
        return vals
    vertices=[];faces=[];rows=100;cols=128
    for i in range(rows+1):
        y=1.59+(2.345-1.59)*i/rows;w,depth,cz=interpolate(y)
        for j in range(cols):
            a=j*math.tau/cols;dx=w*math.sin(a);front=math.cos(a);z=cz-depth*front
            if front>0:
                # Broad soft nasal bridge and rounded tip, without separate primitive seams.
                relief=.035*gauss(dx,y-1.993,.035,.080)+.064*gauss(dx,y-1.893,.044,.050)
                relief+=.022*gauss(abs(dx)-.042,y-1.872,.026,.028)
                relief+=.015*gauss(dx,y-1.775,.103,.035)
                relief+=.017*gauss(abs(dx)-.171,y-1.846,.065,.060)
                relief-=.014*gauss(abs(dx)-.125,y-1.998,.065,.033)
                z-=relief*front**4
            vertices.append((x+dx,y,z))
    for i in range(rows):
        for j in range(cols):
            a=i*cols+j;b=i*cols+(j+1)%cols;faces.append((a,a+cols,b+cols,b))
    faces.extend([tuple(range(cols)),tuple(reversed([rows*cols+j for j in range(cols)]))])
    head=mesh('Continuous oval face',vertices,faces,skin)
    # Small almond eyes with upper/lower lids and restrained visible sclera.
    for side in [-1,1]:
        cx=x+side*.126;cy=1.994;cz=.452
        verts=[(cx,cy,cz-.019)];n=64
        for i in range(n):
            a=i*math.tau/n;dx=.066*math.cos(a);dy=(.034 if math.sin(a)>0 else .027)*math.sin(a)
            verts.append((cx+dx,cy+dy+side*dx*.07,cz))
        mesh('Almond sclera',verts,[(0,1+(i+1)%n,1+i) for i in range(n)],'#eee5db')
        ellipsoid('Dark brown iris',(cx,cy,.429),(.028,.028,.008),'#38271f',bone)
        ellipsoid('Pupil',(cx,cy,.4215),(.011,.013,.003),'#100f10',bone)
        ellipsoid('Eye catchlight',(cx-.007,cy+.008,.4175),(.004,.004,.002),'#f1e7d8',bone)
        upper=[(cx+.066*math.cos(t),cy+.034*math.sin(t)+side*.066*math.cos(t)*.07,.450) for t in [i*math.pi/14 for i in range(15)]]
        lower=[(cx+.066*math.cos(t),cy+.027*math.sin(t)+side*.066*math.cos(t)*.07,.451) for t in [math.pi+i*math.pi/14 for i in range(15)]]
        curve('Upper eyelid',upper,'#af826c',bone,.0027)
        curve('Upper lash line',[(a,b-.001,c-.003) for a,b,c in upper],hair,bone,.0011)
        curve('Lower eyelid',lower,skin,bone,.0022)
        # Brows arch gently and taper at the outside.
        brow=[(x+side*t,y,z) for t,y,z in [(.047,2.090,.463),(.085,2.100,.458),(.128,2.105,.467),(.169,2.102,.480),(.207,2.086,.497)]]
        curve('Natural arched brow',brow,'#33292b',bone,.0055)
        ellipsoid('Ear',(x+side*.293,1.957,.714),(.037,.074,.036),skin,bone)
        ellipsoid('Ear concha',(x+side*.313,1.955,.687),(.012,.039,.009),'#a67965',bone)
        ellipsoid('Gold stud',(x+side*.308,1.902,.676),(.011,.011,.008),'#c9a35e',bone)
    # Closed rose lips: a cupid's bow and fuller lower lip, kept in scale with the face.
    for upper in [True,False]:
        verts=[];n=48
        for i in range(n+1):
            u=-1+2*i/n;dx=.106*u;fade=max(0,1-u*u)**1.1
            seam=1.773+.007*u*u
            thickness=(.014+.004*math.exp(-((abs(u)-.28)/.2)**2)) if upper else .020
            for j in range(5):
                v=j/4;y=seam+(1 if upper else -1)*thickness*fade*v
                z=.447+.050*u*u-.009*math.sin(v*math.pi)*fade
                verts.append((x+dx,y,z))
        fs=[]
        for i in range(n):
            for j in range(4):a=i*5+j;fs.append((a,a+1,a+6,a+5))
        if not upper:fs=[tuple(reversed(f)) for f in fs]
        mesh('Upper lip' if upper else 'Lower lip',verts,fs,'#a36769' if upper else '#b77d7c')
    curve('Mouth seam',[(x+.106*u,1.773+.007*u*u,.445+.050*u*u) for u in [-1+i/16*2 for i in range(17)]],'#8b5558',bone,.0008)
    # Simple thin rounded frames, as requested after the first likeness review.
    if config.get('glasses'):
        for side in [-1,1]:
            pts=[]
            for j in range(33):
                a=j*math.tau/32;c=math.cos(a);s=math.sin(a)
                dx=side*(.138+.103*math.copysign(abs(c)**.8,c))
                pts.append((x+dx,1.994+.064*math.copysign(abs(s)**.8,s),.395+.063*(abs(dx)/.245)**2))
            curve('Simple spectacle rim',pts,'#3b3034',bone,.0034)
            curve('Simple spectacle temple',[(x+side*.239,2.016,.456),(x+side*.303,2.018,.60),(x+side*.311,2.012,.74)],'#3b3034',bone,.003)
        curve('Simple spectacle bridge',[(x-.035,2.014,.397),(x,2.025,.391),(x+.035,2.014,.397)],'#3b3034',bone,.003)
    # Smooth center-parted hair fitted to the scalp, tapering toward the ears.
    verts=[];faces=[];nr=40;nc=128
    for i in range(nr+1):
        for j in range(nc):
            a=j*math.tau/nc;front=math.cos(a)
            limit=.88+(1.95-.88)*(1-front)/2
            phi=.014+(limit-.014)*i/nr
            dx=.307*math.sin(phi)*math.sin(a);y=1.991+.397*math.cos(phi);z=.720-.271*math.sin(phi)*math.cos(a)
            verts.append((x+dx,y,z))
    for i in range(nr):
        for j in range(nc):a=i*nc+j;b=i*nc+(j+1)%nc;faces.append((a,b,b+nc,a+nc))
    cap=mesh('Fitted center-part hair',verts,faces,hair)
    curve('Visible center part',[(x,2.244,.510),(x,2.308,.553),(x,2.365,.631),(x,2.388,.720),(x,2.366,.803)],'#a47d66',bone,.0018)
    # Open-front curtain of loose hair, with smooth tapered face-framing sections.
    rings=[(2.28,.190,.176,.744),(2.16,.270,.247,.752),(2.05,.307,.255,.754),(1.92,.330,.246,.777),
           (1.76,.349,.225,.800),(1.57,.359,.197,.817),(1.38,.350,.162,.827),
           (1.20,.332,.124,.839),(1.13,.295,.085,.850)]
    verts=[];faces=[];nc=64
    for iy,(y,w,d,cz) in enumerate(rings):
        for j in range(nc+1):
            a=.87+(math.tau-1.74)*j/nc
            verts.append((x+w*math.sin(a),y+.010*math.sin(a*3)*(iy/7)**2,cz-d*math.cos(a)))
    for i in range(len(rings)-1):
        for j in range(nc):a=i*(nc+1)+j;faces.append((a,a+1,a+nc+2,a+nc+1))
    curtain=mesh('Loose shoulder length hair',verts,faces,hair)
    sm=curtain.modifiers.new('Soft flowing hair','SUBSURF');sm.levels=2;sm.render_levels=2
    solid=curtain.modifiers.new('Natural hair volume','SOLIDIFY');solid.thickness=.025
    for side in [-1,1]:
        path=[(.165,2.30,.577,.001),(.234,2.20,.576,.023),(.278,2.06,.541,.030),(.306,1.92,.502,.036),
              (.329,1.72,.515,.047),(.333,1.51,.535,.043),(.314,1.32,.567,.032),(.285,1.19,.619,.002)]
        verts=[];faces=[];nc=20
        for dx,y,z,r in path:
            for j in range(nc):
                a=j*math.tau/nc;verts.append((x+side*dx+r*math.cos(a),y,z+r*.55*math.sin(a)))
        for i in range(len(path)-1):
            for j in range(nc):a=i*nc+j;b=i*nc+(j+1)%nc;faces.append((a,b,b+nc,a+nc))
        lock=mesh('Loose face framing hair',verts,faces,hair)
        sm=lock.modifiers.new('Smooth hair fall','SUBSURF');sm.levels=2;sm.render_levels=2
    # Material response remains exportable through Principled BSDF/glTF.
    p=material(skin).node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.55
    p.inputs['Subsurface Weight'].default_value=.055
    p.inputs['Subsurface Radius'].default_value=(1,.42,.24)
    for c in [hair,'#242023','#19171a']:
        p=material(c).node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.58
        p.inputs['Specular IOR Level'].default_value=.22
    for c in ['#b99e77','#c9a35e']:
        p=material(c).node_tree.nodes.get('Principled BSDF');p.inputs['Metallic'].default_value=.72;p.inputs['Roughness'].default_value=.3
