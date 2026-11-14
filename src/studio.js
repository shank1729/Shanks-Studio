import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
export function createStudio(scene, onSelect, loadModel=true) {
  const world = new THREE.Group(); scene.add(world);
  const targets = new Map();
  const mats = {};
  function material(color, glow = false) { const key=color+glow; return mats[key] ||= new THREE.MeshStandardMaterial({color,roughness:.48,metalness:.12,...(glow?{emissive:color,emissiveIntensity:1.4}:{})}); }
  const objects=[];
  function box(name, pos, size, color, id, glow=false) {
    const mesh=new THREE.Mesh(new THREE.BoxGeometry(...size),material(color,glow)); mesh.position.set(...pos); mesh.name=name;mesh.castShadow=true;mesh.receiveShadow=true;mesh.userData.topic=id;world.add(mesh);
    objects.push({name,pos,size,color,id,glow});return mesh;
  }
  function sphere(name,pos,r,color,id,glow=false){const mesh=new THREE.Mesh(new THREE.SphereGeometry(r,32,20),material(color,glow));mesh.position.set(...pos);mesh.name=name;mesh.userData.topic=id;mesh.castShadow=true;world.add(mesh);objects.push({name,pos,r,color,id,glow});return mesh;}
  function anchor(id,pos){const target=new THREE.Object3D();target.position.set(...pos);world.add(target);targets.set(id,target);}
  box('Floating foundation',[0,-.4,0],[6.8,.55,4.6],'#263443');
  box('Warm oak floor',[0,-.08,0],[6.5,.14,4.3],'#8a6658');
  for(let i=0;i<12;i++)box('Floor seam '+i,[-3.1+i*.55,0,0],[.018,.01,4.1],'#5e4944');
  box('Back wall',[0,1.25,-2.12],[6.5,2.6,.15],'#3f4c61');
  box('Side wall',[-3.2,.8,-.65],[.15,1.65,3],'#3f4c61');
  box('Window frame',[1.65,1.5,-2.01],[2.3,1.55,.1],'#202d40');
  box('Window glass',[1.65,1.5,-1.94],[2.12,1.4,.05],'#8491e4',undefined,true);
  box('Window crossbar',[1.65,1.5,-1.86],[.055,1.45,.1],'#293548');
  box('Window sill',[1.65,.74,-1.84],[2.4,.12,.3],'#c3aea0');
  box('Desk top',[-.45,.95,-.45],[3.7,.16,1.3],'#d6ae8d','collab');
  [-2,1.1].forEach(x=>[-.95,.05].forEach(z=>box('Desk leg',[x,.4,z],[.12,1,.12],'#242d3b','collab')));
  box('Laptop base',[-.7,1.08,-.3],[1.25,.07,.75],'#222b3b','collab');
  box('Laptop lid',[-.7,1.53,-.67],[1.3,.85,.07],'#222b3b','collab');
  box('Laptop screen',[-.7,1.53,-.62],[1.15,.7,.018],'#172638','collab');
  for(let i=0;i<6;i++)box('Code line '+i,[-.84+(i%2)*.12,1.78-i*.09,-.6],[.55+(i%3)*.12,.018,.018],i%2?'#9ee5c5':'#bbb5ff','collab',true);
  box('Keyboard',[-.7,1.125,-.22],[.98,.015,.32],'#667287','collab');
  for(let i=0;i<4;i++)box('Key row '+i,[-.7,1.14,-.35+i*.08],[.95,.006,.018],'#252e3c','collab');
  box('Mouse',[.3,1.11,-.12],[.15,.08,.24],'#c7c1bb','collab');
  box('Shelf',[-2.15,1.76,-1.85],[1.5,.12,.45],'#c6a382','java');
  ['#f5b98b','#aaa4db','#9abda9','#ded4ab','#719cc1'].forEach((c,i)=>box('Skill book '+i,[-2.68+i*.24,2.04,-1.85],[.18,.43+(i%2)*.1,.31],c,'java'));
  box('Architecture panel',[-.48,2.03,-2.01],[1.35,.82,.06],'#253146','systems');
  [[-.9,2.18],[-.45,2.18],[-.45,1.86],[0,1.86]].forEach(([x,y],i)=>{box('Diagram node '+i,[x,y,-1.96],[.21,.12,.025],'#a7dacf','systems',true);});
  box('Diagram connection',[-.68,2.18,-1.95],[.25,.014,.01],'#b9a8e5','systems',true);
  box('Diagram link',[-.45,2.01,-1.95],[.014,.32,.01],'#b9a8e5','systems',true);
  box('Diagram connection two',[-.22,1.86,-1.95],[.25,.014,.01],'#b9a8e5','systems',true);
  box('Seat',[0,.58,.98],[.75,.16,.75],'#7470a1','profile');
  box('Seat back',[0,1.12,1.3],[.75,.98,.13],'#7470a1','profile');
  box('Seat stem',[0,.25,.98],[.1,.6,.1],'#232d40','profile');
  box('Seat foot',[0,.03,.98],[.95,.08,.13],'#232d40','profile');
  box('Seat foot cross',[0,.03,.98],[.13,.08,.95],'#232d40','profile');
  box('Side cabinet',[2.45,.48,-.8],[.85,.94,.85],'#bfa484','dsa');
  box('Notebook',[2.45,.99,-.75],[.52,.08,.42],'#dad0ae','dsa');
  box('Notebook band',[2.55,1.035,-.75],[.035,.01,.43],'#9c6b8a','dsa');
  box('Plant pot',[-2.5,.2,1.1],[.48,.45,.48],'#c3a89d');
  for(let i=0;i<6;i++){const leaf=sphere('Plant leaf '+i,[-2.5+Math.sin(i)*.2,.62+i*.075,1.1+Math.cos(i)*.15],.2,'#6fa895');leaf.scale.set(.6,1.8,.6);}
  const bot=new THREE.Group();bot.name='AI companion';bot.position.set(1.7,1.95,.65);world.add(bot);
  const head=sphere('Companion shell',[0,0,0],.33,'#f0e7d6','atlas');world.remove(head);bot.add(head);
  const face=box('Companion face',[0,0,.28],[.43,.22,.13],'#233647','atlas');world.remove(face);bot.add(face);
  [-.11,.11].forEach(x=>{const eye=sphere('Companion eye',[x,.01,.36],.038,'#c5fba9','atlas',true);world.remove(eye);bot.add(eye);});
  const halo=new THREE.Mesh(new THREE.TorusGeometry(.44,.018,8,64),material('#c5fba9',true));halo.rotation.x=Math.PI/2;halo.position.y=-.35;bot.add(halo);
  const lamp=sphere('Desk light',[.85,1.85,-.58],.18,'#ffd19b',undefined,true);box('Lamp stem',[.85,1.45,-.58],[.035,.75,.035],'#303746');box('Lamp base',[.85,1.06,-.58],[.35,.03,.3],'#303746');
  anchor('collab',[-.7,1.85,-.4]);anchor('java',[-2.15,2.4,-1.85]);anchor('systems',[-.48,2.6,-2]);anchor('profile',[0,.7,1.4]);anchor('atlas',[1.7,2.45,.65]);anchor('dsa',[2.45,1.12,-.7]);
  scene.add(new THREE.HemisphereLight('#b8d3fa','#4c334b',2.3));
  const key=new THREE.DirectionalLight('#ffe7c6',4);key.position.set(-3,7,5);key.castShadow=true;key.shadow.mapSize.set(2048,2048);key.shadow.camera.left=-6;key.shadow.camera.right=6;key.shadow.camera.top=6;key.shadow.camera.bottom=-6;scene.add(key);
  const accent=new THREE.PointLight('#9b8cf5',13,9);accent.position.set(2,2,-1);scene.add(accent);
  const glow=new THREE.PointLight('#ffd19b',3,3);glow.position.copy(lamp.position);scene.add(glow);
  let glbLoaded=false,mixer,lastTime;const companionParts=[];
  if(loadModel)new GLTFLoader().load('/models/floating-studio.glb',gltf=>{const model=gltf.scene;model.traverse(obj=>{obj.castShadow=true;obj.receiveShadow=true;const match=notesTopic(obj.name);if(match)obj.userData.topic=match;if(obj.name.startsWith('Companion'))companionParts.push({obj,y:obj.position.y});});world.visible=false;scene.add(model);glbLoaded=true;if(gltf.animations.length){mixer=new THREE.AnimationMixer(model);gltf.animations.forEach(clip=>mixer.clipAction(clip).play());}document.querySelector('#scene')?.setAttribute('data-model','blender');document.querySelector('#scene')?.setAttribute('data-animations',String(gltf.animations.length));},undefined,()=>{});
  function notesTopic(name){return ['collab','java','systems','profile','atlas','dsa'].find(id=>name.endsWith('__'+id));}
  function visible(obj){while(obj){if(!obj.visible)return false;obj=obj.parent;}return true;}
  return {targets,world,update(time,reduced){const delta=lastTime===undefined?0:Math.min(time-lastTime,.1);lastTime=time;if(reduced)return;mixer?.update(delta);if(!glbLoaded){bot.position.y=1.95+Math.sin(time*1.6)*.06;halo.rotation.z=time*.2;}else companionParts.forEach(({obj,y})=>{obj.position.y=y+Math.sin(time*1.6)*.06;});},pick(raycaster){const hit=raycaster.intersectObjects(scene.children,true).find(hit=>hit.object.userData.topic&&visible(hit.object));if(hit)onSelect(hit.object.userData.topic);},objects};
}
