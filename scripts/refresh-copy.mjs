import fs from 'node:fs';
const path='src/main.js';let text=fs.readFileSync(path,'utf8');
text=text.replace('A MAP OF WHAT I BUILD & WHAT I’M LEARNING','WELCOME TO MY LITTLE CORNER OF THE UNIVERSE').replace('Every skill has a story.<br><em>Explore the connections.</em>','Big ideas.<br><em>A little world of my own.</em>').replace('INTERACTIVE KNOWLEDGE GRAPH','THE FLOATING STUDIO · CLICK TO EXPLORE').replace('DRAG TO ORBIT · SCROLL TO ZOOM','DRAG TO LOOK AROUND · CLICK AN OBJECT').replace('Reset graph view','Reset studio view').replace('3D is unavailable in this browser.','The 3D studio is unavailable in this browser.');
fs.writeFileSync(path,text);
