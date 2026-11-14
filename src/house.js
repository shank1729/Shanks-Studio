import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import './house.css';
import portfolio from './portfolio-content.json';

const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
const rooms={
  about:{label:'Meet Shankholi',object:'The front porch',target:[1.1,1.9,3.4],camera:[2.4,3.4,9.8],title:portfolio.profile.tagline,text:portfolio.profile.intro,items:portfolio.about,tag:'01 / THE FRONT PORCH'},
  projects:{label:'Projects',object:'The project cupboard',target:[-2.7,1.9,-2.0],camera:[-1.7,2.8,3.7],title:'A cupboard full of ideas.',text:'Every object on these shelves has a story. Open a project to see what went into making it.',tag:'02 / THE PROJECT ARCHIVE'},
  skills:{label:'Skills',object:'The workbench',target:[1.65,2.0,-2],camera:[3.4,3.4,3.1],title:'Tools of the trade.',text:'The tools behind my backend services, cloud workflows, and production troubleshooting.',items:portfolio.skills,tag:'03 / THE WORKBENCH'},
  experience:{label:'Journey',object:'The memory wall',target:[1.55,3.50,-2.75],camera:[1.6,4.0,2.1],title:'Built in the real world.',text:'From event-driven workflows to production reliability—my work at Tata Consultancy Services.',items:portfolio.experience.highlights,tag:'04 / THE MEMORY WALL'},
  education:{label:'Learning',object:'The bookshelf',target:[-4.05,2.6,-.3],camera:[.0,3.7,3.7],title:'Always another chapter.',text:'My foundation in information technology, with a growing focus on cloud engineering and generative AI.',tag:'05 / THE BOOKSHELF'},
  contact:{label:'Say hello',object:'The mailbox',target:[3.87,1.7,3.3],camera:[6.3,3.0,8.3],title:'Good things start with hello.',text:'Passionate about technology, a leetcode problem, or an idea to share? I’d love to hear about it.',tag:'06 / THE MAILBOX'}
};
const projects=Object.fromEntries(portfolio.projectOrder.map(id=>[id,portfolio.projects[id]]));
document.querySelector('#app').innerHTML=`
  <div id="world" aria-label="Interactive 3D cutaway home"></div>
  <header><a href="#" class="wordmark" aria-label="Return home">shanks<span>.</span><small>PERSONAL SPACE / 001</small></a><div class="top-actions"><span class="status"><i></i> AT HOME</span></div></header>
  <section class="welcome" id="welcome"><span class="eyebrow">SHANKHOLI RAY / SOFTWARE ENGINEER</span><h1>A little home.<br><em>A world of ideas.</em></h1></section>
  <div id="hint" role="status">Drag to look around · Choose an object to explore</div>
  <nav aria-label="Explore the house" class="room-nav"><button data-room="home" class="active"><span>⌂</span>Home</button>${Object.entries(rooms).map(([id,r],i)=>`<button data-room="${id}"><span>${String(i+1).padStart(2,'0')}</span>${r.label}</button>`).join('')}</nav>
  <div class="scene-caption"><span>SHANKS STUDIO</span><span><a href="/credits.html" target="_blank" rel="noopener">SPRING RIG / BLENDER FOUNDATION · CC-BY</a></span></div>
  <div id="hover-label" hidden></div>
  <aside id="story" aria-labelledby="story-title" hidden><button id="close-story" aria-label="Return to the whole house">← Back home <span>Esc</span></button><div id="story-body"></div></aside>
  <div id="loading"><div class="load-icon">⌂</div><span class="eyebrow">A SMALL PLACE WITH BIG IDEAS</span><h2>Make yourself at home</h2><div class="load-track"><i id="load-fill"></i></div><p id="load-status">Getting ready to welcome you</p><button id="enter" hidden>Come on in <span>↗</span></button></div>
  <div id="fallback" hidden><h2>The house couldn’t load.</h2><p>You can still explore the portfolio using the navigation below.</p><button id="retry">Try again</button></div>`;
const host=document.querySelector('#world'), story=document.querySelector('#story'), body=document.querySelector('#story-body');
let current='home', activeProject=null, ambient=!reduced, cabinet=null, mixer=null, transition=null, renderer, camera, controls, scene, composer;
let pointerDown=null, hovered=null, model=null, loadReady=false;
const animatedDoors=[];
const escape=text=>String(text).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function links(items){return `<div class="profile-links">${items.filter(l=>/^(https:\/\/|mailto:)/.test(l.url)).map(l=>`<a href="${escape(l.url)}"${l.url.startsWith('https:')?' target="_blank" rel="noopener noreferrer"':''}>${escape(l.label)} <span aria-hidden="true">↗</span></a>`).join('')}</div>`;}
const contactLinks=()=>[{label:'Email me',url:`mailto:${portfolio.profile.email}`},...portfolio.profile.links];
function content(id){
  const r=rooms[id];
  story.dataset.room=id;
  delete story.dataset.project;
  const {experience:work,education:school,certifications,achievements}=portfolio;
  let extra='';
  if(id==='projects')extra=`<div class="project-list" aria-label="Choose a project">${Object.entries(projects).map(([key,p],i)=>`<button data-project="${escape(key)}"><span class="project-number">${String(i+1).padStart(2,'0')}</span><span><small>${escape(p.type)}</small><strong>${escape(p.name)}</strong></span><b aria-hidden="true">↗</b></button>`).join('')}</div>`;
  else if(id==='education')extra=`<div class="education-card"><span class="period">${escape(school.period)}</span><h3>${escape(school.institution)}</h3><p>${escape(school.degree)}</p><strong class="grade">${escape(school.grade)}</strong></div><h3 class="section-label">PROBLEM SOLVING</h3>${achievements.map(a=>`<div class="achievement-card"><strong>${escape(a.value)}</strong><span>${escape(a.label)}</span>${links([a.link])}</div>`).join('')}<h3 class="section-label">CERTIFICATIONS</h3><div class="story-items">${certifications.map(c=>`<section><h3>${escape(c.name)}</h3><p>${escape(c.detail)}</p></section>`).join('')}</div>`;
  else if(id==='contact')extra=`<p class="contact-name">${escape(portfolio.profile.name)}<br><span>${escape(portfolio.profile.headline)}</span></p><a class="contact-email" href="mailto:${escape(portfolio.profile.email)}">${escape(portfolio.profile.email)}</a>${links(contactLinks())}`;
  else extra=`${id==='about'?`<div class="profile-role">${escape(portfolio.profile.personalNote)}</div>`:''}${id==='experience'?`<div class="career-card"><span class="period">${escape(work.period)}</span><h3>${escape(work.role)}</h3><p>${escape(work.company)}</p><span class="career-focus">${escape(work.focus)}</span></div><div class="impact-grid">${work.metrics.map(m=>`<div><strong>${escape(m.value)}</strong><span>${escape(m.label)}</span></div>`).join('')}</div>`:''}<div class="story-items">${r.items.map(([h,p])=>`<section><h3>${escape(h)}</h3><p>${escape(p)}</p></section>`).join('')}</div>${id==='about'?links(contactLinks()):''}`;
  body.innerHTML=`<div class="eyebrow">${r.tag}</div><h2 id="story-title" tabindex="-1">${escape(r.title)}</h2>${id==='about'?`<p class="intro-greeting">${escape(portfolio.profile.greeting)}</p>`:''}<p class="intro-copy">${escape(r.text)}</p>${extra}`;
  body.querySelectorAll('[data-project]').forEach(el=>el.addEventListener('click',()=>selectProject(el.dataset.project)));
  story.scrollTop=0;
}
function selectProject(id){
  if(!projects[id])return;
  if(current!=='projects')go('projects');
  activeProject=id;const p=projects[id];
  story.dataset.project=id;
  body.innerHTML=`<button class="back-to-projects" id="back-to-projects">← All projects</button><article id="project-detail" class="project-detail project-focus"><span class="eyebrow">${escape(p.type)}</span><div class="project-title-row">${p.icon?`<img class="project-icon" src="${escape(p.icon)}" width="42" height="42" alt="">`:''}<h2 id="story-title" tabindex="-1">${escape(p.name)}</h2></div><p>${escape(p.text)}</p>${links(p.links)}<div class="tech-stack">${p.stack.map(s=>`<span>${escape(s)}</span>`).join('')}</div><p>${escape(p.details)}</p><ul class="project-highlights">${p.highlights.map(h=>`<li>${escape(h)}</li>`).join('')}</ul></article>`;
  body.querySelector('#back-to-projects').addEventListener('click',()=>{
    activeProject=null;content('projects');
    body.querySelector('#story-title').focus({preventScroll:true});
  });
  story.scrollTop=0;
  body.querySelector('#story-title').focus({preventScroll:true});
}
function go(id){
  if(id!=='home'&&!rooms[id])return;
  current=id;activeProject=null;document.querySelectorAll('[data-room]').forEach(b=>b.classList.toggle('active',b.dataset.room===id));
  document.querySelector('#welcome').classList.toggle('away',id!=='home');document.querySelector('#hint').hidden=id!=='home';
  story.hidden=id==='home';
  if(id!=='home')content(id);
  if(!camera||!controls)return;
  frameForPanel();
  const small=innerWidth<720;
  const target=new THREE.Vector3(...(id==='home'?[0,2.0,0]:rooms[id].target));
  let destination=new THREE.Vector3(...(id==='home'?[12,10.3,17]:rooms[id].camera));
  if(id==='home'&&innerWidth/innerHeight<1)destination.sub(target).multiplyScalar(1.35).add(target);
  if(small&&id!=='home')destination.sub(target).multiplyScalar(1.35).add(target);
  transition={start:performance.now(),from:camera.position.clone(),to:destination,fromTarget:controls.target.clone(),toTarget:target};
  controls.enabled=false;
}
function frameForPanel(){
  if(!camera||!host.clientWidth||!host.clientHeight)return;
  const w=host.clientWidth,h=host.clientHeight;
  if(current==='home')camera.clearViewOffset();
  else if(w<600)camera.setViewOffset(w,h,0,h*.23,w,h);
  else camera.setViewOffset(w,h,Math.min(190,w*.15),0,w,h);
  camera.updateProjectionMatrix();
}
document.querySelectorAll('[data-room]').forEach(el=>el.addEventListener('click',()=>go(el.dataset.room)));
document.querySelector('.wordmark').addEventListener('click',e=>{e.preventDefault();go('home');});
document.querySelector('#close-story').addEventListener('click',()=>go('home'));
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&current!=='home')go('home');});
document.querySelector('#enter').addEventListener('click',()=>{document.querySelector('#loading').classList.add('finished');go('home');});
document.querySelector('#retry').addEventListener('click',()=>location.reload());
function ready(){loadReady=true;document.querySelector('#load-fill').style.width='100%';document.querySelector('#enter').hidden=false;}
function fail(error){console.error('House loading failed',error);document.querySelector('#loading').hidden=true;document.querySelector('#fallback').hidden=false;}

try{
  scene=new THREE.Scene();scene.background=new THREE.Color('#070d17');scene.fog=new THREE.FogExp2('#070d17',.018);
  camera=new THREE.PerspectiveCamera(38,1,.1,160);camera.position.set(17,14,23);
  renderer=new THREE.WebGLRenderer({antialias:true,powerPreference:'high-performance'});renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));
  renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.25;host.append(renderer.domElement);
  controls=new OrbitControls(camera,renderer.domElement);controls.target.set(0,2,0);controls.enableDamping=true;controls.enablePan=false;controls.minDistance=3;controls.maxDistance=32;controls.maxPolarAngle=Math.PI*.47;controls.minPolarAngle=.35;
  controls.addEventListener('start',()=>{if(transition){transition=null;controls.enabled=true;}});
  scene.add(new THREE.HemisphereLight(0x9bd9ff,0x101329,2));
  function light(color,intensity,position){const l=new THREE.DirectionalLight(color,intensity);l.position.set(...position);scene.add(l);return l;}
  const key=light(0x85d9ff,3,[5,10,7]);key.castShadow=true;key.shadow.mapSize.set(2048,2048);key.shadow.camera.left=-9;key.shadow.camera.right=9;key.shadow.camera.top=9;key.shadow.camera.bottom=-9;key.shadow.normalBias=.035;
  light(0xb768ff,3,[-4,6,-3]);light(0xffc18b,1.3,[-1,5,1]);
  const roomLight=new THREE.PointLight(0xffbb77,35,10,2);roomLight.position.set(0,3.2,0);scene.add(roomLight);
  const cyanLight=new THREE.PointLight(0x00d9ff,30,14,2);cyanLight.position.set(-4,2,4);scene.add(cyanLight);
  const purpleLight=new THREE.PointLight(0x952aff,40,16,2);purpleLight.position.set(5,2,1);scene.add(purpleLight);
  const ground=new THREE.Mesh(new THREE.PlaneGeometry(200,200),new THREE.MeshStandardMaterial({color:0x07131e,metalness:.45,roughness:.4}));ground.rotation.x=-Math.PI/2;ground.position.y=-.08;ground.receiveShadow=true;scene.add(ground);
  composer=new EffectComposer(renderer);composer.addPass(new RenderPass(scene,camera));composer.addPass(new UnrealBloomPass(new THREE.Vector2(1,1),.33,.55,1.25));composer.addPass(new OutputPass());
  const draco=new DRACOLoader();draco.setDecoderPath('/draco/');
  const loader=new GLTFLoader();loader.setDRACOLoader(draco);
  loader.load('/models/cyber-home.glb',gltf=>{
    model=gltf.scene;scene.add(model);
    model.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;}if(o.name.startsWith('cupboard_hinge_'))animatedDoors.push({o,base:o.rotation.y,side:o.name.endsWith('L')?-1:1});});
    if(gltf.animations.length){mixer=new THREE.AnimationMixer(model);gltf.animations.forEach(clip=>mixer.clipAction(clip).play());}
    ready();
  },ev=>{if(ev.total)document.querySelector('#load-fill').style.width=`${Math.max(10,ev.loaded/ev.total*95)}%`;},fail);
  const ray=new THREE.Raycaster(),mouse=new THREE.Vector2();
  function hit(e){const rect=renderer.domElement.getBoundingClientRect();mouse.set((e.clientX-rect.left)/rect.width*2-1,-(e.clientY-rect.top)/rect.height*2+1);ray.setFromCamera(mouse,camera);const h=model?ray.intersectObject(model,true)[0]:null;if(!h)return null;let o=h.object;while(o){const id=o.name.split('__')[1]?.replace(/\.\d+$/,'');if(id)return id==='profile'?'about':id;o=o.parent;}return null;}
  renderer.domElement.addEventListener('pointerdown',e=>{pointerDown=[e.clientX,e.clientY];});
  renderer.domElement.addEventListener('pointerup',e=>{if(!pointerDown||Math.hypot(e.clientX-pointerDown[0],e.clientY-pointerDown[1])>6)return;const id=hit(e);if(projects[id])selectProject(id);else if(id==='learning')go('education');else if(rooms[id])go(id);});
  renderer.domElement.addEventListener('pointermove',e=>{const id=hit(e);hovered=id;const label=document.querySelector('#hover-label');const name=rooms[id]?.object||projects[id]?.name||(id==='learning'?'Learning archive':null);label.hidden=!name;label.textContent=name||'';label.style.left=`${Math.min(innerWidth-230,e.clientX+18)}px`;label.style.top=`${e.clientY-40}px`;renderer.domElement.style.cursor=name?'pointer':'grab';});
  renderer.domElement.addEventListener('pointerleave',()=>{document.querySelector('#hover-label').hidden=true;});
  const resize=()=>{const w=host.clientWidth,h=host.clientHeight;camera.aspect=w/h;frameForPanel();renderer.setSize(w,h);composer.setSize(w,h);};new ResizeObserver(resize).observe(host);resize();
  let last=performance.now();
  function tick(now){requestAnimationFrame(tick);const dt=Math.min((now-last)/1000,.05);last=now;
    if(transition){const t=Math.min(1,(now-transition.start)/(reduced?1:1450));const ease=t*t*(3-2*t);camera.position.lerpVectors(transition.from,transition.to,ease);controls.target.lerpVectors(transition.fromTarget,transition.toTarget,ease);if(t===1){transition=null;controls.enabled=true;}}
    controls.update();
    if(ambient)mixer?.update(dt);
    for(const d of animatedDoors){const target=d.base+(current==='projects'?d.side*1.65:0);d.o.rotation.y=THREE.MathUtils.damp(d.o.rotation.y,target,reduced?100:4.5,dt);}
    composer.render();
  }requestAnimationFrame(tick);
}catch(e){fail(e);}
