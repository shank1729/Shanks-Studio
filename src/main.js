import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { notes } from './knowledge.js';
import { createStudio } from './studio.js';
import './style.css';

document.querySelector('#app').innerHTML = `
<header><a class="brand" href="#">s<span>●</span> <b>PORTFOLIO ATLAS</b></a><nav><button class="nav-active" id="explore">Explore</button><button id="about">About this atlas ↗</button></nav><span class="build-status"><i></i> BUILDING IN PUBLIC</span></header>
<main><section class="intro"><div class="eyebrow">WELCOME TO MY LITTLE CORNER OF THE UNIVERSE</div><h1>Big ideas.<br><em>A little world of my own.</em></h1><p>I’m Shank. This is my corner of the internet —<br>projects, ideas, and the engineering that connects them.</p></section>
<section class="workspace"><div class="graph-panel"><div class="graph-top"><span><i class="live-dot"></i> THE FLOATING STUDIO · CLICK TO EXPLORE</span><button id="reset" aria-label="Reset studio view">↺ Reset view</button></div><div id="scene"><div id="labels"></div><div id="fallback" hidden>The 3D studio is unavailable in this browser. Explore the same notes using the buttons below.</div></div><div class="graph-bottom"><div class="legend"><span><i class="project"></i> Projects</span><span><i class="skill"></i> Skills</span><span><i class="learning"></i> Learning</span></div><span>DRAG TO LOOK AROUND · CLICK AN OBJECT</span></div><div id="node-list" aria-label="Portfolio topics"></div></div>
<aside><div class="assistant-heading"><div class="assistant-icon">✳</div><div><h2>Ask about me</h2><span>Follow the evidence. Find the fit.</span></div><span class="badge">PREVIEW</span></div><div class="mode-row"><span class="mode">Profile explorer</span><span>LOCAL RETRIEVAL</span></div><div id="messages" aria-live="polite"><div class="message"><span class="message-label">ATLAS GUIDE</span><p>Hi, I’m your guide to this portfolio. Explore a project, ask about my backend work, or see what I’m learning.</p><p class="muted">Answers come from the notes in this atlas. AI generation is coming next.</p></div></div><div class="suggestions"><button data-question="What is your strongest project?">Show the main project ↗</button><button data-question="What are your Java backend skills?">Explore backend skills ↗</button><button data-question="What are you learning?">What’s next? ↗</button></div><form id="ask-form"><label class="sr-only" for="question">Ask a question about this portfolio</label><input id="question" placeholder="Ask about projects, skills, or learning…" maxlength="400" required><button aria-label="Send question">↑</button></form><div class="assistant-footer">GROUNDED IN NOTES <span>✧</span> NO INVENTED EXPERIENCE</div></aside></section>
<section class="detail"><div><span class="eyebrow" id="detail-kind"></span><h2 id="detail-title"></h2></div><div><p id="detail-text"></p><span id="detail-source"></span></div></section></main><footer><span>SHANK / PORTFOLIO ATLAS</span><span>A living portfolio. A little more connected.</span><span>VERSION 0.1 ↗</span></footer>`;

const labels = document.querySelector('#labels');
const meshMap = new Map(); const labelMap = new Map();
let selected = 'profile';
function select(id) {
  selected = id; const note = notes.find(n => n.id === id);
  document.querySelector('#detail-kind').textContent = note.kind;
  document.querySelector('#detail-title').textContent = note.title;
  document.querySelector('#detail-text').textContent = note.detail;
  document.querySelector('#detail-source').textContent = note.source;
  labelMap.forEach((el,key) => {el.classList.toggle('selected',key===id);el.setAttribute('aria-pressed',String(key===id));});
}
notes.forEach((note,index) => {
  const button = document.createElement('button'); button.className='node-label'; button.style.setProperty('--node-color',note.color);button.dataset.marker=String(index+1).padStart(2,'0');button.title=note.title;button.setAttribute('aria-label',note.title);
  const kind=document.createElement('span');kind.textContent=note.kind;const name=document.createElement('strong');name.textContent=note.title;
  button.append(kind,name);button.addEventListener('click',()=>select(note.id));labels.append(button);labelMap.set(note.id,button);
  const compact=document.createElement('button');compact.textContent=note.title;compact.addEventListener('click',()=>select(note.id));document.querySelector('#node-list').append(compact);
});
select('profile');
try {
  const host=document.querySelector('#scene');const scene=new THREE.Scene();const camera=new THREE.PerspectiveCamera(38,1,.1,100);camera.position.set(9,7.5,11);
  const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));host.prepend(renderer.domElement);
  renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1;
  const controls=new OrbitControls(camera,renderer.domElement);controls.target.set(0,1,0);controls.enableDamping=true;controls.minDistance=9;controls.maxDistance=23;controls.enablePan=false;controls.minPolarAngle=.25;controls.maxPolarAngle=Math.PI*.49;controls.minAzimuthAngle=-.6;controls.maxAzimuthAngle=1.5;controls.update();
  const studio=createStudio(scene,select);studio.targets.forEach((obj,id)=>meshMap.set(id,obj));
  const raycaster=new THREE.Raycaster(), pointer=new THREE.Vector2();let down;
  renderer.domElement.addEventListener('pointerdown',e=>{down=[e.clientX,e.clientY];});
  renderer.domElement.addEventListener('pointerup',e=>{if(!down||Math.hypot(e.clientX-down[0],e.clientY-down[1])>5)return;const rect=renderer.domElement.getBoundingClientRect();pointer.set((e.clientX-rect.left)/rect.width*2-1,-(e.clientY-rect.top)/rect.height*2+1);raycaster.setFromCamera(pointer,camera);studio.pick(raycaster);});
  new ResizeObserver(()=>{const w=host.clientWidth,h=host.clientHeight;renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();}).observe(host);
  document.querySelector('#reset').addEventListener('click',()=>{camera.position.set(9,7.5,11);controls.target.set(0,1,0);controls.update();select('profile');});
  const vector=new THREE.Vector3();const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;function animate(time=0){requestAnimationFrame(animate);controls.update();studio.update(time/1000,reduced);meshMap.forEach((mesh,id)=>{mesh.getWorldPosition(vector);vector.project(camera);const el=labelMap.get(id);el.style.left=`${Math.max(el.offsetWidth/2+8,Math.min(host.clientWidth-el.offsetWidth/2-8,(vector.x*.5+.5)*host.clientWidth))}px`;el.style.top=`${(-vector.y*.5+.5)*host.clientHeight+12}px`;el.hidden=vector.z>1;});renderer.render(scene,camera);}animate();select('profile');
}catch(error){document.querySelector('#fallback').hidden=false;labels.hidden=true;console.warn('3D fallback:',error.message);}

function addMessage(text,label){const el=document.createElement('div');el.className='message';const heading=document.createElement('span');heading.className='message-label';heading.textContent=label;const body=document.createElement('p');body.textContent=text;el.append(heading,body);document.querySelector('#messages').append(el);return el;}
function answer(question){addMessage(question,'YOU');const words=question.toLowerCase().match(/[a-z]+/g)||[];const ranked=notes.filter(n=>n.id!=='profile').map(note=>({note,score:words.reduce((sum,w)=>sum+(note.tags.includes(w)?1:0),0)})).filter(x=>x.score>0).sort((a,b)=>b.score-a.score);const results=ranked.slice(0,2);
  if(!results.length){addMessage('I don’t have enough information in the current notes to answer that. Try asking about the collaboration project, Java, system design, or this portfolio. CV and work experience details still need to be added.','ATLAS GUIDE');}
  else {select(results[0].note.id);const el=addMessage(results.map(x=>x.note.detail).join('\n\n'),'ATLAS GUIDE');results.forEach(({note})=>{const cite=document.createElement('button');cite.className='source';cite.textContent=`↗ ${note.source}`;cite.addEventListener('click',()=>select(note.id));el.append(cite);});}
  const box=document.querySelector('#messages');box.scrollTop=box.scrollHeight;
}
document.querySelector('#ask-form').addEventListener('submit',e=>{e.preventDefault();const input=document.querySelector('#question');const value=input.value.trim();if(value){answer(value);input.value='';}});
document.querySelectorAll('[data-question]').forEach(button=>button.addEventListener('click',()=>answer(button.dataset.question)));
document.querySelector('#about').addEventListener('click',()=>{select('atlas');document.querySelector('.detail').scrollIntoView({behavior:'smooth',block:'center'});});
document.querySelector('#explore').addEventListener('click',()=>document.querySelector('.workspace').scrollIntoView({behavior:'smooth'}));
