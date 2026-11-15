// Gallery of all 151 animas and the cast of characters. Uses ANIMAS and CAST from data.js.
(()=>{
const $=id=>document.getElementById(id),grid=$('dex-grid'),info=$('dex-info'),chips=$('dex-chips'),cast=$('cast-grid');
if(!grid)return;
const TC={Ember:'#e8602c',Tide:'#3f8fe0',Bloom:'#58b94a',Volt:'#f2c824',Stone:'#a68a64',Gale:'#8fc8e8',Frost:'#9fe0ea',Shade:'#6d4fa3',Lumen:'#f4dc7a',Venom:'#b04fb0',Iron:'#8c98a8',Wild:'#c9a27a'};
const STATS=['HP','ATK','DEF','SPD','SPC'],pad=n=>String(n).padStart(3,'0');
const pos=(id,s)=>(-((id-1)%16)*s)+'px '+(-Math.floor((id-1)/16)*s)+'px';
const typeChip=t=>'<span class="tchip"><i style="background:'+TC[t]+'"></i>'+t+'</span>';
let filter='All',sel=ANIMAS[0];
function show(a){sel=a;
 const evo=a.evolves_to?'Evolves into <b>'+ANIMAS[a.evolves_to-1].name+'</b> at Lv '+a.evolve_level+'.':(a.stages>1?'Final form.':'');
 info.innerHTML='<div class="big" style="background-position:'+pos(a.id,128)+'" role="img" aria-label="'+a.name+'"></div>'
  +'<div class="meta"><span class="no">No.'+pad(a.id)+'</span><h3>'+a.name+'</h3><div>'+a.types.map(typeChip).join(' ')+'</div></div>'
  +'<p class="txt">'+a.dex+'</p><p class="txt evo">'+evo+'</p>'
  +STATS.map((n,i)=>'<div class="stat"><span>'+n+'</span><div><b style="width:'+Math.round(a.stats[i]/160*100)+'%"></b></div><span>'+a.stats[i]+'</span></div>').join('');
 grid.querySelectorAll('.an').forEach(b=>b.classList.toggle('sel',+b.dataset.id===a.id))}
function render(){grid.innerHTML='';
 ANIMAS.filter(a=>filter==='All'||a.types.includes(filter)).forEach(a=>{const b=document.createElement('button');
  b.className='an';b.dataset.id=a.id;b.title=pad(a.id)+' '+a.name;b.setAttribute('aria-label',a.name);
  b.style.backgroundPosition=pos(a.id,64);b.addEventListener('click',()=>show(a));grid.appendChild(b)});
 chips.querySelectorAll('button').forEach(c=>c.classList.toggle('on',c.dataset.t===filter));show(sel)}
['All'].concat(Object.keys(TC)).forEach(t=>{const b=document.createElement('button');b.dataset.t=t;
 const n=t==='All'?ANIMAS.length:ANIMAS.filter(a=>a.types.includes(t)).length;b.textContent=t+' '+n;
 b.addEventListener('click',()=>{filter=t;render()});chips.appendChild(b)});
render();
CAST.forEach(c=>{const f=document.createElement('figure');f.className='who';
 f.innerHTML='<div style="background-position:0 '+(-c.row*64)+'px" role="img" aria-label="'+c.name+'"></div><figcaption>'+c.name+'<small>'+c.role+'</small></figcaption>';cast.appendChild(f)});
})();
