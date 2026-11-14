import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
r=bpy.data.objects['RIG-Spring']
result=[]
for p in r.pose.bones:
    if (('arm' in p.name or 'hand' in p.name) and len(p.keys())) or p.name in ['arm_fk_L','arm_fk_R','forearm_fk_L','forearm_fk_R','arm_ik_L','arm_ik_R'] or p.name.startswith(('head','neck')):
        result.append({'name':p.name,'props':{k:str(p[k]) for k in p.keys()},'head':list(p.head),'tail':list(p.tail),'rotation_mode':p.rotation_mode,'rotation':list(p.rotation_euler),'constraints':[{'type':c.type,'name':c.name,'influence':c.influence} for c in p.constraints]})
(ROOT/'assets/spring-source/rig-info.json').write_text(json.dumps(result,indent=2))
print('RIG_INFO_COMPLETE')
