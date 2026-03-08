// ================================================
//   MINTO HOLIDAYS - MAIN JAVASCRIPT
// ================================================

// ── HERO SLIDER (3 seconds) ──
(function(){
  const slides = document.querySelectorAll('.slide');
  const dotsEl = document.getElementById('dots');
  if(!slides.length) return;
  let cur = 0, timer;

  if(dotsEl){
    slides.forEach((_,i)=>{
      const d = document.createElement('button');
      d.className = 'dot' + (i===0 ? ' active' : '');
      d.onclick = ()=>{ go(i); reset(); };
      dotsEl.appendChild(d);
    });
  }

  function go(n){
    slides[cur].classList.remove('active');
    if(dotsEl) dotsEl.children[cur].classList.remove('active');
    cur = n;
    slides[cur].classList.add('active');
    if(dotsEl) dotsEl.children[cur].classList.add('active');
  }

  function next(){ go((cur+1) % slides.length); }
  function reset(){ clearInterval(timer); timer = setInterval(next, 3000); }

  timer = setInterval(next, 3000);

  const hero = document.querySelector('.hero');
  if(hero){
    hero.addEventListener('mouseenter', ()=> clearInterval(timer));
    hero.addEventListener('mouseleave', reset);
  }
})();

// ── HAMBURGER MENU ──
function toggleMenu(){
  document.getElementById('menu')?.classList.toggle('open');
}
document.addEventListener('click', e => {
  const m = document.getElementById('menu');
  const h = document.querySelector('.ham');
  if(m && h && !m.contains(e.target) && !h.contains(e.target))
    m.classList.remove('open');
});

// ── BOOKING TABS ──
function showTab(name){
  document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('on'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('on'));
  document.getElementById('tab-'+name)?.classList.add('on');
  const idx = {tours:0, hotels:1, flights:2, trains:3}[name];
  document.querySelectorAll('.tab-btn')[idx]?.classList.add('on');
}

// ── ROUND TRIP TOGGLE ──
document.querySelectorAll('input[name="ftrip"]').forEach(r => {
  r.addEventListener('change', function(){
    const g = document.getElementById('retGrp');
    if(g) g.style.display = this.value==='round' ? 'block' : 'none';
  });
});

// ── SWAP ──
function swapFlights(){
  const a=document.getElementById('ff'), b=document.getElementById('ft');
  if(a&&b) [a.value,b.value]=[b.value,a.value];
}
function swapTrains(){
  const a=document.getElementById('tf'), b=document.getElementById('tt');
  if(a&&b) [a.value,b.value]=[b.value,a.value];
}

// ── SEARCH: TOURS ──
function searchTours(){
  const tour = document.getElementById('st')?.value;
  if(!tour){ toast('Please select a tour package','e'); return; }
  window.location.href = 'book.html?tour=' + encodeURIComponent(tour);
}

// ── SEARCH: HOTELS ──
function searchHotels(){
  const city = document.getElementById('hcity')?.value;
  const ci   = document.getElementById('hci')?.value;
  const co   = document.getElementById('hco')?.value;
  if(!city){ toast('Please enter a city','e'); return; }
  if(!ci||!co){ toast('Please select check-in and check-out dates','e'); return; }
  const list = [
    {n:`The Grand ${city}`,     r:'★★★★★', p:'₹4,500/night', am:'Free WiFi · Pool · Breakfast · Spa'},
    {n:`${city} Comfort Inn`,   r:'★★★★',  p:'₹2,800/night', am:'Free WiFi · Restaurant · Parking'},
    {n:`Budget Stay ${city}`,   r:'★★★',   p:'₹1,200/night', am:'Free WiFi · AC · 24hr Reception'},
    {n:`${city} Palace Resort`, r:'★★★★★', p:'₹8,200/night', am:'Pool · Spa · Fine Dining · Gym'},
    {n:`City Center ${city}`,   r:'★★★★',  p:'₹3,100/night', am:'Rooftop · Bar · Parking'},
  ];
  let h = `<h3>Hotels in ${city}</h3><p style="color:#888;font-size:13px;margin:6px 0 16px">${ci} → ${co} · ${document.getElementById('hguests')?.value||'2 Adults'}</p><div class="res-list">`;
  list.forEach(i => {
    h += `<div class="res-item" onclick="openBookModal('hotel','${i.n}')">
      <div><h4>🏨 ${i.n}</h4><p>${i.r}</p><p style="font-size:12px;margin-top:3px">${i.am}</p></div>
      <div style="text-align:right"><div class="res-price">${i.p}</div><span class="avail">Available</span></div>
    </div>`;
  });
  h += '</div>';
  openModal(h,'hotel');
}

// ── SEARCH: FLIGHTS ──
function searchFlights(){
  const fr = document.getElementById('ff')?.value;
  const to = document.getElementById('ft')?.value;
  const dt = document.getElementById('fd')?.value;
  const cl = document.getElementById('fc')?.value || 'Economy';
  if(!fr||!to){ toast('Please enter departure and destination','e'); return; }
  if(!dt){ toast('Please select a date','e'); return; }
  const al = [
    {n:'IndiGo 6E-124',    dep:'06:00',arr:'08:15',dur:'2h 15m',p:'₹3,249',st:'Non-Stop'},
    {n:'Air India AI-864', dep:'08:30',arr:'10:50',dur:'2h 20m',p:'₹3,849',st:'Non-Stop'},
    {n:'SpiceJet SG-117',  dep:'11:00',arr:'13:30',dur:'2h 30m',p:'₹2,899',st:'Non-Stop'},
    {n:'Vistara UK-812',   dep:'14:45',arr:'17:05',dur:'2h 20m',p:'₹4,499',st:'Non-Stop'},
    {n:'GoAir G8-219',     dep:'18:00',arr:'21:30',dur:'3h 30m',p:'₹2,349',st:'1 Stop'},
  ];
  let h = `<h3>✈️ Flights: ${fr} → ${to}</h3><p style="color:#888;font-size:13px;margin:6px 0 16px">${dt} · ${cl}</p><div class="res-list">`;
  al.forEach(a => {
    h += `<div class="res-item" onclick="openBookModal('flight','${a.n} | ${fr} to ${to}')">
      <div><h4>${a.n}</h4><p>${a.dep} → ${a.arr} &nbsp;|&nbsp; ${a.dur}</p>
      <p style="margin-top:4px"><span class="avail">${a.st}</span></p></div>
      <div style="text-align:right"><div class="res-price">${a.p}</div><small style="color:#888">per person</small></div>
    </div>`;
  });
  h += '</div>';
  openModal(h,'flight');
}

// ── SEARCH: TRAINS ──
function searchTrains(){
  const fr = document.getElementById('tf')?.value;
  const to = document.getElementById('tt')?.value;
  const dt = document.getElementById('td')?.value;
  const cl = document.getElementById('tc')?.value || 'Sleeper';
  if(!fr||!to){ toast('Please enter departure and destination stations','e'); return; }
  if(!dt){ toast('Please select travel date','e'); return; }
  const trains = [
    {n:'Rajdhani Express', num:'12951',dep:'16:25',arr:'08:15',dur:'15h 50m',av:'Available',seats:24,p:'₹1,840'},
    {n:'Shatabdi Express', num:'12001',dep:'06:00',arr:'13:20',dur:'7h 20m', av:'Available',seats:8, p:'₹1,245'},
    {n:'Duronto Express',  num:'12213',dep:'23:00',arr:'14:30',dur:'15h 30m',av:'WL 12',   seats:0, p:'₹1,560'},
    {n:'Garib Rath',       num:'12909',dep:'15:35',arr:'07:25',dur:'15h 50m',av:'Available',seats:42,p:'₹720'},
    {n:'Gujarat Express',  num:'19011',dep:'19:45',arr:'12:30',dur:'16h 45m',av:'RAC 5',   seats:5, p:'₹640'},
  ];
  let h = `<h3>🚂 Trains: ${fr} → ${to}</h3><p style="color:#888;font-size:13px;margin:6px 0 16px">${dt} · ${cl}</p><div class="res-list">`;
  trains.forEach(t => {
    const col = t.av==='Available'?'#2e7d32':t.av.startsWith('WL')?'#c62828':'#e65100';
    h += `<div class="res-item" onclick="openBookModal('train','${t.n} | ${fr} to ${to}')">
      <div><h4>🚂 ${t.n} (${t.num})</h4>
      <p>${t.dep} → ${t.arr} &nbsp;|&nbsp; ${t.dur}</p>
      <p style="color:${col};font-weight:700;font-size:13px;margin-top:3px">${t.av}
      ${t.seats>0?`<span style="color:#888;font-weight:400;margin-left:8px;font-size:12px">${t.seats} seats</span>`:''}</p></div>
      <div style="text-align:right"><div class="res-price">${t.p}</div><small style="color:#888">per person</small></div>
    </div>`;
  });
  h += '</div>';
  openModal(h,'train');
}

// ── MODAL ──
let _mType = '';
function openModal(html, type){
  _mType = type;
  const m  = document.getElementById('modal');
  const mc = document.getElementById('modal-content');
  const mf = document.getElementById('modal-form');
  if(!m) return;
  mc.innerHTML = html;
  if(mf) mf.style.display = 'none';
  m.classList.add('show');
}
function openBookModal(type, detail){
  _mType = type;
  const d = document.getElementById('m-detail');
  const f = document.getElementById('modal-form');
  if(d) d.value = detail;
  if(f){ f.style.display = 'block'; f.scrollIntoView({behavior:'smooth'}); }
}
function closeModal(){
  document.getElementById('modal')?.classList.remove('show');
}
document.addEventListener('click', e => {
  const m = document.getElementById('modal');
  if(m && e.target===m) closeModal();
});

// ── SUBMIT BOOKING ──
async function submitBooking(){
  const name  = document.getElementById('m-name')?.value.trim();
  const email = document.getElementById('m-email')?.value.trim();
  const phone = document.getElementById('m-phone')?.value.trim();
  const detail= document.getElementById('m-detail')?.value;
  if(!name||!phone){ toast('Please fill your name and mobile number','e'); return; }

  const endpoints = {
    hotel:  '/api/book-hotel',
    flight: '/api/book-flight',
    train:  '/api/book-train',
    tours:  '/api/book-tour',
  };
  const payload = {name,email,phone,detail,type:_mType,timestamp:new Date().toISOString()};

  try{
    await fetch(endpoints[_mType]||'/api/book-tour',{
      method:'POST', headers:{'Content-Type':'application/json'},
      body:JSON.stringify(payload)
    });
  }catch(e){}

  closeModal();
  toast('✅ Booking confirmed! Our team will contact you within 2 hours.');
}

// ── SEARCH FILTER (homepage cards) ──
const si    = document.getElementById('srch');
const cards = document.querySelectorAll('.card[data-t]');
if(si && cards.length){
  si.addEventListener('keyup', ()=>{
    const v = si.value.toLowerCase();
    cards.forEach(c => { c.style.display = (!v || c.dataset.t.includes(v)) ? '' : 'none'; });
  });
}

// ── STATS COUNTER ──
const statSec = document.querySelector('.stats-sec');
if(statSec){
  const obs = new IntersectionObserver(entries => {
    entries.forEach(en => {
      if(en.isIntersecting){
        document.querySelectorAll('.stat-n[data-n]').forEach(el => {
          const target = +el.dataset.n;
          let c = 0;
          const step = target / (2000/16);
          const t = setInterval(()=>{
            c += step;
            if(c >= target){ el.textContent = target.toLocaleString()+'+'; clearInterval(t); }
            else el.textContent = Math.floor(c).toLocaleString();
          }, 16);
        });
        obs.unobserve(en.target);
      }
    });
  }, {threshold:.3});
  obs.observe(statSec);
}

// ── TOAST ──
function toast(msg, type=''){
  const t = document.getElementById('toast');
  if(!t) return;
  t.textContent = msg;
  t.className = 'toast' + (type==='e' ? ' err' : '');
  t.classList.add('show');
  setTimeout(()=> t.classList.remove('show'), 3600);
}
