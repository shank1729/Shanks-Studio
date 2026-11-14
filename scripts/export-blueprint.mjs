import * as THREE from 'three';
import fs from 'node:fs';
import { createStudio } from '../src/studio.js';
const scene=new THREE.Scene();createStudio(scene,()=>{},false);scene.updateMatrixWorld(true);
const shapes=[];scene.traverse(obj=>{if(!obj.isMesh)return;shapes.push({name:obj.name+(obj.userData.topic?'__'+obj.userData.topic:''),type:obj.geometry.type,parameters:obj.geometry.parameters,matrix:obj.matrixWorld.toArray(),color:obj.material.color.toArray(),emission:obj.material.emissive.toArray(),emissionStrength:obj.material.emissiveIntensity});});
fs.writeFileSync('scripts/studio-blueprint.json',JSON.stringify(shapes,null,2));
