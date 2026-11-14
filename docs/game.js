// Animas: Ember browser demo: a JavaScript port of the Godot game's starter town.
// Uses the same tileset and Animas Pixel font as the real game.
(()=>{
const TS=16,VW=240,VH=160,MOVE=.2,DX=[0,1,0,-1],DY=[-1,0,1,0];
const cv=document.getElementById('c'),ctx=cv.getContext('2d');ctx.imageSmoothingEnabled=false;
const img=new Image(),fontImg=new Image();let fontDark;
const FM={"32":[1,1,0,3],"33":[9,1,1,2],"34":[17,1,3,4],"35":[25,1,5,6],"36":[33,1,5,6],"37":[41,1,5,6],"38":[49,1,5,6],"39":[57,1,1,2],"40":[65,1,3,4],"41":[73,1,3,4],"42":[81,1,5,6],"43":[89,1,5,6],"44":[97,1,1,2],"45":[105,1,4,5],"46":[113,1,1,2],"47":[121,1,5,6],"48":[1,12,5,6],"49":[9,12,3,4],"50":[17,12,5,6],"51":[25,12,5,6],"52":[33,12,5,6],"53":[41,12,5,6],"54":[49,12,5,6],"55":[57,12,5,6],"56":[65,12,5,6],"57":[73,12,5,6],"58":[81,12,1,2],"59":[89,12,1,2],"60":[97,12,3,4],"61":[105,12,5,6],"62":[113,12,3,4],"63":[121,12,5,6],"64":[1,23,5,6],"65":[9,23,5,6],"66":[17,23,5,6],"67":[25,23,5,6],"68":[33,23,5,6],"69":[41,23,5,6],"70":[49,23,5,6],"71":[57,23,5,6],"72":[65,23,5,6],"73":[73,23,3,4],"74":[81,23,5,6],"75":[89,23,5,6],"76":[97,23,5,6],"77":[105,23,5,6],"78":[113,23,5,6],"79":[121,23,5,6],"80":[1,34,5,6],"81":[9,34,5,6],"82":[17,34,5,6],"83":[25,34,5,6],"84":[33,34,5,6],"85":[41,34,5,6],"86":[49,34,5,6],"87":[57,34,5,6],"88":[65,34,5,6],"89":[73,34,5,6],"90":[81,34,5,6],"91":[89,34,3,4],"92":[97,34,5,6],"93":[105,34,3,4],"94":[113,34,3,4],"95":[121,34,5,6],"96":[1,45,2,3],"97":[9,45,5,6],"98":[17,45,5,6],"99":[25,45,5,6],"100":[33,45,5,6],"101":[41,45,5,6],"102":[49,45,5,6],"103":[57,45,5,6],"104":[65,45,5,6],"105":[73,45,1,2],"106":[81,45,3,4],"107":[89,45,4,5],"108":[97,45,3,4],"109":[105,45,5,6],"110":[113,45,5,6],"111":[121,45,5,6],"112":[1,56,5,6],"113":[9,56,5,6],"114":[17,56,5,6],"115":[25,56,5,6],"116":[33,56,4,5],"117":[41,56,5,6],"118":[49,56,5,6],"119":[57,56,5,6],"120":[65,56,5,6],"121":[73,56,5,6],"122":[81,56,5,6],"123":[89,56,4,5],"124":[97,56,1,2],"125":[105,56,4,5],"126":[113,56,5,6]};
const gm=c=>FM[c.charCodeAt(0)]||FM[63];
const tw=s=>{let w=0;for(const c of s)w+=gm(c)[3];return w};
function drawText(s,x,y,n){for(const c of s){if(n--<=0)break;const m=gm(c);if(m[2])ctx.drawImage(fontDark,m[0],m[1],m[2],9,x,y,m[2],9);x+=m[3]}}
const T={'.':[0,0],',':[1,0],f:[2,0],g:[3,0],p:[4,0],s:[5,0],w:[6,0],T:[0,1],b:[1,1],F:[2,1],S:[3,1],'#':[4,1],_:[5,1],c:[6,1],R:[7,1],r:[0,2],H:[1,2],W:[2,2],D:[3,2],m:[4,2],C:[5,2],B:[6,2],L:[7,2]};
const SOLID=new Set('wTbFS#RrHWCBL'.split(''));
const MAPS={
town:{rows:[
"TTTTTTTTTTTTTTTTTTTTTTTT","T..,..f.....,.....gggg.T","T.....RRRR.........ggg.T","T.f...RRRR...,.....ggg.T",
"T.....HWHH...........g.T","T.....HDHH......b......T","T,....pp..............,T","T.....pppppppppppppp..sT",
"T..f..pp......S.......sT","T.....pp........ff..wwwT","T..,..pp..g.g.......wwwT","T.....pp..ggg.....,.wwwT",
"T.....pp..ggg..........T","T.....pp..............bT","T.....pp...............T","TTTTTTTTTTTTTTTTTTTTTTTT"],
npcs:[{x:10,y:6,dir:2,body:'#4a7bd0',hair:'#3a2a1a',lines:['Nice day for an adventure!','The path east leads to Route 1... someday.']},
{x:9,y:11,dir:1,body:'#d0884a',hair:'#222',lines:['Wild creatures hide in the tall grass.','Walk through it and see what happens!']}],
warps:{'7,5':['house',4,6,0]}},
house:{rows:["##########","#BBB__BBB#","#________#","#__cccc__#","#__cccc__#","#________#","#________#","####m#####"],
npcs:[{x:2,y:5,dir:1,body:'#c0508a',hair:'#6a3a1a',lines:['Welcome to my house!','This demo mirrors your Godot project.']}],
warps:{'4,7':['town',7,6,2]}}};
let cur,mw,mh;const P={x:0,y:0,dir:2,t:0,mv:false,turn:0};
let dlg=null,lock=false,aPress=false;const fade={a:0,to:0,cb:null},held=[false,false,false,false];
function load(n,x,y,d){cur=MAPS[n];mw=cur.rows[0].length;mh=cur.rows.length;P.x=x;P.y=y;P.dir=d;P.mv=false}
const tileAt=(x,y)=>(x<0||y<0||x>=mw||y>=mh)?'T':cur.rows[y][x];
const npcAt=(x,y)=>cur.npcs.find(n=>n.x===x&&n.y===y);
const blocked=(x,y)=>SOLID.has(tileAt(x,y))||!!npcAt(x,y);
const say=l=>{dlg={lines:l,i:0,n:0}};
const heldDir=()=>held.findIndex(Boolean);
function stepped(){
 const w=cur.warps[P.x+','+P.y];
 if(w){lock=true;fade.to=1;fade.cb=()=>{load(...w);fade.to=0;fade.cb=()=>{lock=false}};return}
 if(tileAt(P.x,P.y)==='g'&&Math.random()<.2)say(['A wild creature appeared!','(Battles arrive in Phase 4.)']);
}
function update(dt){
 if(fade.a!==fade.to){const up=fade.to>fade.a;fade.a+=(up?1:-1)*dt/.25;
  if(up?fade.a>=fade.to:fade.a<=fade.to){fade.a=fade.to;const cb=fade.cb;fade.cb=null;if(cb)cb()}}
 if(lock){aPress=false;return}
 if(dlg){const L=dlg.lines[dlg.i];dlg.n=Math.min(L.length,dlg.n+dt*45);
  if(aPress){aPress=false;if(dlg.n<L.length)dlg.n=L.length;else if(++dlg.i>=dlg.lines.length)dlg=null;else dlg.n=0}return}
 if(P.mv){P.t+=dt;if(P.t>=MOVE){P.mv=false;P.x+=DX[P.dir];P.y+=DY[P.dir];stepped()}return}
 if(P.turn>0){P.turn-=dt;return}
 if(aPress){aPress=false;const tx=P.x+DX[P.dir],ty=P.y+DY[P.dir],n=npcAt(tx,ty);
  if(n){n.dir=(P.dir+2)%4;say(n.lines)}else if(tileAt(tx,ty)==='S')say(['Welcome to Pixel Town!','Population: you.']);return}
 const d=heldDir();if(d<0)return;
 if(d!==P.dir){P.dir=d;P.turn=.1;return}
 if(!blocked(P.x+DX[d],P.y+DY[d])){P.mv=true;P.t=0}
}
function person(x,y,dir,body,hair,bob){
 y-=bob;const sk='#f0c8a0';
 ctx.fillStyle='#2a2a30';ctx.fillRect(x+4,y+13,3,3);ctx.fillRect(x+9,y+13,3,3);
 ctx.fillStyle=body;ctx.fillRect(x+3,y+7,10,6);
 ctx.fillStyle=sk;ctx.fillRect(x+4,y+1,8,7);
 ctx.fillStyle=hair;ctx.fillRect(x+4,y,8,dir===0?7:3);
 ctx.fillStyle='#222';
 if(dir===2){ctx.fillRect(x+5,y+5,1,2);ctx.fillRect(x+10,y+5,1,2)}
 else if(dir===3)ctx.fillRect(x+5,y+5,1,2);else if(dir===1)ctx.fillRect(x+10,y+5,1,2);
}
function wrap(s){const out=[];let l='';for(const w of s.split(' ')){const t=l?l+' '+w:w;if(tw(t)>216&&l){out.push(l);l=w}else l=t}out.push(l);return out}
function draw(now){
 ctx.fillStyle='#000';ctx.fillRect(0,0,VW,VH);
 const f=P.mv?P.t/MOVE:0,px=(P.x+DX[P.dir]*f)*TS,py=(P.y+DY[P.dir]*f)*TS;
 const cl=(v,m)=>Math.round(Math.max(0,Math.min(m-VW<0?0:v,m)));
 let cx=mw*TS<=VW?(mw*TS-VW)/2:Math.max(0,Math.min(mw*TS-VW,px+TS/2-VW/2));
 let cy=mh*TS<=VH?(mh*TS-VH)/2:Math.max(0,Math.min(mh*TS-VH,py+TS/2-VH/2));
 cx=Math.round(cx);cy=Math.round(cy);
 for(let y=0;y<mh;y++)for(let x=0;x<mw;x++){const t=T[cur.rows[y][x]];ctx.drawImage(img,t[0]*TS,t[1]*TS,TS,TS,x*TS-cx,y*TS-cy,TS,TS)}
 for(const n of cur.npcs)person(n.x*TS-cx,n.y*TS-cy,n.dir,n.body,n.hair,0);
 person(Math.round(px)-cx,Math.round(py)-cy,P.dir,'#d04a4a','#2a2a5a',P.mv&&Math.floor(P.t*10)%2?1:0);
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
let ready=0;const go=()=>{if(++ready<2)return;
 fontDark=document.createElement('canvas');fontDark.width=fontImg.width;fontDark.height=fontImg.height;
 const fc=fontDark.getContext('2d');fc.drawImage(fontImg,0,0);fc.globalCompositeOperation='source-in';fc.fillStyle='#202020';fc.fillRect(0,0,fontDark.width,fontDark.height);
 load('town',7,6,0);say(['Welcome to Animas: Ember!','Move with the arrow keys or D-pad. Press Enter or A to talk. Try the house!']);requestAnimationFrame(frame)};
img.onload=go;fontImg.onload=go;img.src='assets/tiles.png';fontImg.src='assets/animas_pixel.png';
})();
