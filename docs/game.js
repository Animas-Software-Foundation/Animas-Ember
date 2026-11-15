// Animas: Ember browser demo: a JavaScript port of the Godot game's overworld
// (movement, NPCs, trainers with line of sight, wild animas). Maps, roster, cast, and font
// metrics come from data.js, which tools/build_site_data.py generates from the game's own files.
(()=>{
const TS=16,VW=240,VH=160,MOVE=.2,DX=[0,1,0,-1],DY=[-1,0,1,0];
const ATLAS_DIR=[1,3,0,2]; // demo direction (0 up, 1 right, 2 down, 3 left) -> characters.png direction (down, up, left, right)
const cv=document.getElementById('c'),ctx=cv.getContext('2d');ctx.imageSmoothingEnabled=false;
const img=new Image(),fontImg=new Image(),chars=new Image(),animas=new Image();let fontDark;
const ROW={},CNAME={};CAST.forEach(c=>{ROW[c.id]=c.row;CNAME[c.id]=c.name});
const idOf=n=>ANIMAS.findIndex(a=>a.name===n)+1;
const gm=c=>FM[c.charCodeAt(0)]||FM[63];
const tw=s=>{let w=0;for(const c of s)w+=gm(c)[3];return w};
function drawText(s,x,y,n,src){src=src||fontDark;for(const c of s){if(n--<=0)break;const m=gm(c);if(m[2])ctx.drawImage(src,m[0],m[1],m[2],9,x,y,m[2],9);x+=m[3]}}
const T={'.':[0,0],',':[1,0],f:[2,0],g:[3,0],p:[4,0],s:[5,0],w:[6,0],T:[0,1],b:[1,1],F:[2,1],S:[3,1],'#':[4,1],_:[5,1],c:[6,1],R:[7,1],r:[0,2],H:[1,2],W:[2,2],D:[3,2],m:[4,2],C:[5,2],B:[6,2],L:[7,2]};
const SOLID=new Set('wTbFS#RrHWCBL'.split(''));
// directions: 0 up, 1 right, 2 down, 3 left
const MAPS={
 town:{rows:MAP_ROWS.town,warps:{'7,5':['house',4,6,0],'23,7':['route1',1,7,1]},
  enc:[['Nutkin',2,4,30],['Chirpa',2,4,30],['Snuffle',2,4,25],['Tadgle',2,3,15]],
  npcs:[{x:10,y:6,dir:2,look:'kid_boy',lines:['Nice day for an adventure!','The path east leads to Route 1. Watch out for trainers!']},
   {x:9,y:11,dir:1,look:'gardener',lines:['Wild animas hide in the tall grass.','Walk through it and see who shows up!']},
   {x:16,y:3,dir:3,look:'elder',lines:['Welcome to Pixel Town, young one.','There are 151 animas out there. In the full game, press Esc to open your Animadex.']},
   {x:2,y:9,dir:1,look:'granny',lines:['When I was young, I only knew of a handful of animas.','Now they say there are 151 species!']},
   {x:12,y:4,dir:2,look:'shopkeeper',lines:['The shop is still being built.','Come back in a later update!']},
   {x:18,y:10,dir:1,look:'fisher',lines:["The fish aren't biting today.",'Maybe I should try the pond over there.']},
   {x:14,y:8,dir:2,hidden:1,lines:['Welcome to Pixel Town!','Route 1 is to the east.']}]},
 house:{rows:MAP_ROWS.house,warps:{'4,7':['town',7,6,2]},
  npcs:[{x:2,y:5,dir:1,look:'mom',lines:['Welcome home! Be careful out there.','Remember: your Animadex fills up as you meet new animas.']},
   {x:6,y:2,dir:2,look:'professor',lines:["I'm Professor Cinder. I study animas.",'151 species have been recorded. Can you meet them all?']},
   {x:7,y:5,dir:3,look:'student',lines:["I'm taking notes for the Professor.",'Trainers on Route 1 will battle you on sight!']}]},
 route1:{rows:MAP_ROWS.route1,warps:{'0,7':['town',22,7,3]},
  enc:[['Fidget',2,4,25],['Chirpa',2,4,20],['Snuffle',3,5,20],['Nutkin',3,5,15],['Hopper',4,6,10],['Puffling',3,5,10]],
  npcs:[{x:14,y:9,dir:0,look:'hiker',lines:['Hiking builds character. And sore legs.','Trainers on this route will challenge you if you walk in front of them!']},
   {x:27,y:6,dir:2,hidden:1,lines:['Route 1','The road ends here for now. More of the world is coming soon!']}],
  trainers:[{id:'pim',x:9,y:5,dir:2,range:4,look:'netter',lines:["You walked right into my net! Let's battle!"],after:['My bugs are the best... usually.'],team:[['Fidget',3],['Sparkbug',4]]},
   {id:'nell',x:16,y:10,dir:0,range:4,look:'scout',lines:['Scouts never miss a thing. Ready?'],after:["Great teamwork. I'm taking notes."],team:[['Snuffle',4],['Sproutle',5]]},
   {id:'ty',x:24,y:6,dir:2,range:3,look:'camper',lines:["I've been camping out here all week. Battle time!"],after:['Time to go home and rest.'],team:[['Cindle',5],['Zaplet',5]]}]}};
let cur,curName,mw,mh;const P={x:0,y:0,dir:2,t:0,mv:false,turn:0,step:0};
let dlg=null,lock=false,busy=false,aPress=false,overlay=null,bubble=null,waits=[];
const fade={a:0,to:0,cb:null},held=[false,false,false,false];
function load(n,x,y,d){curName=n;cur=MAPS[n];mw=cur.rows[0].length;mh=cur.rows.length;P.x=x;P.y=y;P.dir=d;P.mv=false}
const ents=()=>cur.npcs.concat(cur.trainers||[]);
const tileAt=(x,y)=>(x<0||y<0||x>=mw||y>=mh)?'T':cur.rows[y][x];
const npcAt=(x,y)=>ents().find(n=>n.x===x&&n.y===y);
const blocked=(x,y)=>SOLID.has(tileAt(x,y))||!!npcAt(x,y);
const sleep=s=>new Promise(r=>waits.push([s,r]));
const say=l=>new Promise(r=>{dlg={lines:l,i:0,n:0,r}});
const heldDir=()=>held.findIndex(Boolean);
function sees(t){const d=t.dir,dx=P.x-t.x,dy=P.y-t.y;let dist=0;
 if(DX[d]&&dy===0&&Math.sign(dx)===DX[d])dist=Math.abs(dx);else if(DY[d]&&dx===0&&Math.sign(dy)===DY[d])dist=Math.abs(dy);
 if(dist<1||dist>t.range)return false;
 for(let i=1;i<dist;i++)if(blocked(t.x+DX[d]*i,t.y+DY[d]*i))return false;return true}
async function battle(t){await say(t.lines);const name=CNAME[t.look];overlay={look:t.look,team:t.team,title:name};
 await say([name+' sent out '+t.team[0][0]+' (Lv '+t.team[0][1]+')!','(Battles arrive in a later update. You win by default!)']);overlay=null;t.beat=true}
async function challenge(t){busy=true;bubble=t;await sleep(.6);bubble=null;
 const n=Math.max(Math.abs(P.x-t.x),Math.abs(P.y-t.y))-1;
 for(let i=0;i<n;i++){t.anim=1+i%2;await new Promise(r=>{t.w=0;t.res=r})}
 t.anim=0;P.dir=(t.dir+2)%4;await battle(t);busy=false}
async function wild(){busy=true;const e=pickEnc(cur.enc),id=idOf(e[0]),lv=e[1]+Math.floor(Math.random()*(e[2]-e[1]+1)),a=ANIMAS[id-1];
 overlay={id,title:e[0]+'   Lv '+lv};
 await say(['A wild '+e[0]+' appeared!','It is a '+a.types.join('/')+' anima. (Battles arrive in a later update.)']);overlay=null;busy=false}
function pickEnc(t){let r=Math.random()*t.reduce((s,e)=>s+e[3],0);for(const e of t){r-=e[3];if(r<0)return e}return t[0]}
function stepped(){
 const w=cur.warps[P.x+','+P.y];
 if(w){lock=true;fade.to=1;fade.cb=()=>{load(...w);fade.to=0;fade.cb=()=>{lock=false}};return}
 for(const t of cur.trainers||[])if(!t.beat&&sees(t)){challenge(t);return}
 if(cur.enc&&tileAt(P.x,P.y)==='g'&&Math.random()<.2)wild();
}
function update(dt){
 waits=waits.filter(w=>{w[0]-=dt;if(w[0]<=0){w[1]();return false}return true});
 for(const t of cur.trainers||[])if(t.w!==undefined){t.w+=dt;if(t.w>=.18){t.x+=DX[t.dir];t.y+=DY[t.dir];t.w=undefined;t.res()}}
 if(fade.a!==fade.to){const up=fade.to>fade.a;fade.a+=(up?1:-1)*dt/.25;
  if(up?fade.a>=fade.to:fade.a<=fade.to){fade.a=fade.to;const cb=fade.cb;fade.cb=null;if(cb)cb()}}
 if(lock){aPress=false;return}
 if(dlg){const L=dlg.lines[dlg.i];dlg.n=Math.min(L.length,dlg.n+dt*45);
  if(aPress){aPress=false;if(dlg.n<L.length)dlg.n=L.length;else if(++dlg.i>=dlg.lines.length){const r=dlg.r;dlg=null;r()}else dlg.n=0}return}
 if(busy){aPress=false;return}
 if(P.mv){P.t+=dt;if(P.t>=MOVE){P.mv=false;P.x+=DX[P.dir];P.y+=DY[P.dir];stepped()}return}
 if(P.turn>0){P.turn-=dt;return}
 if(aPress){aPress=false;const tx=P.x+DX[P.dir],ty=P.y+DY[P.dir],n=npcAt(tx,ty);
  if(n){if(!n.hidden)n.dir=(P.dir+2)%4;if(n.team){if(n.beat)say(n.after);else{busy=true;battle(n).then(()=>{busy=false})}}else say(n.lines)}
  return}
 const d=heldDir();if(d<0)return;
 if(d!==P.dir){P.dir=d;P.turn=.1;return}
 if(!blocked(P.x+DX[d],P.y+DY[d])){P.mv=true;P.t=0;P.step++}
}
const person=(x,y,dir,look,anim)=>ctx.drawImage(chars,(ATLAS_DIR[dir]*3+anim)*16,ROW[look]*16,16,16,x,y,16,16);
const sprite=(id,x,y,s)=>ctx.drawImage(animas,((id-1)%16)*32,Math.floor((id-1)/16)*32,32,32,x,y,s,s);
function wrap(s){const out=[];let l='';for(const w of s.split(' ')){const t=l?l+' '+w:w;if(tw(t)>216&&l){out.push(l);l=w}else l=t}out.push(l);return out}
function draw(now){
 ctx.fillStyle='#000';ctx.fillRect(0,0,VW,VH);
 const f=P.mv?P.t/MOVE:0,px=(P.x+DX[P.dir]*f)*TS,py=(P.y+DY[P.dir]*f)*TS;
 let cx=mw*TS<=VW?(mw*TS-VW)/2:Math.max(0,Math.min(mw*TS-VW,px+TS/2-VW/2));
 let cy=mh*TS<=VH?(mh*TS-VH)/2:Math.max(0,Math.min(mh*TS-VH,py+TS/2-VH/2));
 cx=Math.round(cx);cy=Math.round(cy);
 for(let y=0;y<mh;y++)for(let x=0;x<mw;x++){const t=T[cur.rows[y][x]];ctx.drawImage(img,t[0]*TS,t[1]*TS,TS,TS,x*TS-cx,y*TS-cy,TS,TS)}
 for(const n of ents()){if(n.hidden)continue;
  const o=n.w!==undefined?n.w/.18:0,ex=Math.round((n.x+DX[n.dir]*o)*TS)-cx,ey=Math.round((n.y+DY[n.dir]*o)*TS)-cy;
  person(ex,ey,n.dir,n.look,n.anim||0);
  if(bubble===n){ctx.fillStyle='#221a2c';ctx.fillRect(ex+4,ey-11,7,8);ctx.fillRect(ex+7,ey-3,1,2);ctx.fillStyle='#fff';ctx.fillRect(ex+5,ey-10,5,6);ctx.fillStyle='#d8402c';ctx.fillRect(ex+7,ey-9,1,3);ctx.fillRect(ex+7,ey-5,1,1)}}
 person(Math.round(px)-cx,Math.round(py)-cy,P.dir,'hero',P.mv?1+P.step%2:0);
 if(overlay){ctx.fillStyle='#1d1a2b';ctx.fillRect(0,0,VW,VH);
  if(overlay.id)sprite(overlay.id,72,2,96);
  else{ctx.drawImage(chars,0,ROW[overlay.look]*16,16,16,88,6,64,64);const n=overlay.team.length,x0=(VW-n*36)/2;overlay.team.forEach((m,i)=>sprite(idOf(m[0]),x0+i*36+2,70,32))}
  drawText(overlay.title,Math.floor((VW-tw(overlay.title))/2),98,99,fontImg)}
 if(fade.a>0){ctx.fillStyle='rgba(0,0,0,'+fade.a+')';ctx.fillRect(0,0,VW,VH)}
 if(dlg){ctx.fillStyle='#fff';ctx.fillRect(4,108,232,48);ctx.strokeStyle='#3b3b3b';ctx.lineWidth=2;ctx.strokeRect(5,109,230,46);
  const L=dlg.lines[dlg.i];let r=Math.floor(dlg.n);wrap(L).forEach((ln,i)=>{drawText(ln,12,115+i*11,r);r-=ln.length+1});
  if(dlg.n>=L.length&&Math.floor(now/400)%2){ctx.fillStyle='#202020';[[222,144,7],[223,145,5],[224,146,3],[225,147,1]].forEach(a=>ctx.fillRect(a[0],a[1],a[2],1))}}
}
const KD={ArrowUp:0,w:0,ArrowRight:1,d:1,ArrowDown:2,s:2,ArrowLeft:3,a:3};
cv.addEventListener('keydown',e=>{const k=e.key.length===1?e.key.toLowerCase():e.key;
 if(Object.hasOwn(KD,k)){held[KD[k]]=true;e.preventDefault()}else if(k==='Enter'||k===' '||k==='z'){if(!e.repeat)aPress=true;e.preventDefault()}});
cv.addEventListener('keyup',e=>{const k=e.key.length===1?e.key.toLowerCase():e.key;if(Object.hasOwn(KD,k))held[KD[k]]=false});
document.querySelectorAll('[data-d]').forEach(b=>{const d=+b.dataset.d;
 b.addEventListener('pointerdown',e=>{held[d]=true;b.setPointerCapture(e.pointerId)});
 ['pointerup','pointercancel'].forEach(t=>b.addEventListener(t,()=>{held[d]=false}))});
document.getElementById('A').addEventListener('pointerdown',()=>{aPress=true});
cv.addEventListener('contextmenu',e=>e.preventDefault());
let last=0;function frame(t){const dt=Math.min(.05,(t-last)/1000||0);last=t;update(dt);draw(t);requestAnimationFrame(frame)}
cv.tabIndex=0;cv.addEventListener('pointerdown',()=>cv.focus());
window.__demo=()=>({map:curName,x:P.x,y:P.y,busy,beat:(cur.trainers||[]).filter(t=>t.beat).length}); // read-only state, used by tests
let ready=0;const go=()=>{if(++ready<4)return;
 fontDark=document.createElement('canvas');fontDark.width=fontImg.width;fontDark.height=fontImg.height;
 const fc=fontDark.getContext('2d');fc.drawImage(fontImg,0,0);fc.globalCompositeOperation='source-in';fc.fillStyle='#202020';fc.fillRect(0,0,fontDark.width,fontDark.height);
 load('town',7,6,0);say(['Welcome to Animas: Ember!','Move with the arrow keys or D-pad. Press Enter or A to talk. Try the house, or head east to Route 1!']);requestAnimationFrame(frame)};
[img,fontImg,chars,animas].forEach(i=>{i.onload=go});
img.src='assets/tiles.png';fontImg.src='assets/animas_pixel.png';chars.src='assets/characters.png';animas.src='assets/animas.png';
})();
