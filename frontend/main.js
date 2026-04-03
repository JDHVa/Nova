/* ══════════════════════════════════════════════════════════════
   NOVA — Frontend Logic
══════════════════════════════════════════════════════════════ */
const API = '';   // empty = relative to server; set to 'http://localhost:8000' if opening index.html directly
 
/* ── State ─────────────────────────────────────────────────── */
let lang      = 'es';
let chatHistory = [];
let currentFile = null;
let sending    = false;
 
/* ══════════════════════════════════════════════════════════════
   PARTICLE CANVAS
══════════════════════════════════════════════════════════════ */
(function(){
  const canvas = document.getElementById('canvas');
  const ctx    = canvas.getContext('2d');
  let particles = [];
  const N = 70;
 
  function resize(){
    canvas.width  = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  window.addEventListener('resize', resize);
  resize();
 
  function rand(a,b){ return Math.random()*(b-a)+a; }
 
  function init(){
    particles = [];
    for(let i=0;i<N;i++){
      particles.push({
        x: rand(0,canvas.width),
        y: rand(0,canvas.height),
        vx: rand(-.25,.25),
        vy: rand(-.25,.25),
        r: rand(1.5,3),
        alpha: rand(.3,.8),
      });
    }
  }
  init();
 
  function draw(){
    ctx.clearRect(0,0,canvas.width,canvas.height);
 
    // Lines
    for(let i=0;i<particles.length;i++){
      for(let j=i+1;j<particles.length;j++){
        const dx = particles[i].x-particles[j].x;
        const dy = particles[i].y-particles[j].y;
        const dist = Math.sqrt(dx*dx+dy*dy);
        if(dist<130){
          ctx.beginPath();
          ctx.moveTo(particles[i].x,particles[i].y);
          ctx.lineTo(particles[j].x,particles[j].y);
          ctx.strokeStyle = `rgba(0,212,247,${(1-dist/130)*0.12})`;
          ctx.lineWidth = .8;
          ctx.stroke();
        }
      }
    }
 
    // Dots
    particles.forEach(p=>{
      ctx.beginPath();
      ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
      ctx.fillStyle = `rgba(0,212,247,${p.alpha})`;
      ctx.fill();
 
      p.x += p.vx; p.y += p.vy;
      if(p.x<0)p.x=canvas.width;
      if(p.x>canvas.width)p.x=0;
      if(p.y<0)p.y=canvas.height;
      if(p.y>canvas.height)p.y=0;
    });
 
    requestAnimationFrame(draw);
  }
  draw();
})();
 
/* ══════════════════════════════════════════════════════════════
   i18n
══════════════════════════════════════════════════════════════ */
const T = {
  welcome_es: `¡Hola! Soy **NOVA**, tu asistente médico con IA. 🩺
 
Estoy aquí para ayudarte con:
• Información sobre síntomas y condiciones de salud
• Recomendaciones de medicamentos (genéricos y de marca)
• Qué hacer y qué NO hacer ante distintas situaciones
• Orientación sobre cuándo acudir al médico
 
Puedes indicarme tu **presupuesto** para darte opciones adecuadas. ¿En qué puedo ayudarte hoy?`,
 
  welcome_en: `Hello! I'm **NOVA**, your AI medical assistant. 🩺
 
I'm here to help you with:
• Information about symptoms and health conditions
• Medication recommendations (generic and brand-name)
• What to DO and NOT do in different situations
• Guidance on when to see a doctor
 
You can tell me your **budget** for tailored options. How can I help you today?`,
 
  quick1_es: 'Tengo fiebre de 38°C y dolor de cabeza desde ayer. ¿Qué me recomiendas?',
  quick1_en: 'I have a fever of 38°C (100.4°F) and headache since yesterday. What do you recommend?',
  quick2_es: 'Me duele el pecho cuando respiro profundo. ¿Qué puede ser y qué debo hacer?',
  quick2_en: 'My chest hurts when I breathe deeply. What could it be and what should I do?',
  quick3_es: 'Tengo gripa con moco, estornudos y algo de fiebre. ¿Qué medicamento me recomiendas?',
  quick3_en: 'I have a cold with runny nose, sneezing and some fever. What medication do you recommend?',
  quick4_es: 'No puedo dormir bien, me desvelo y me levanto cansado. ¿Qué me ayudaría?',
  quick4_en: "I can't sleep well, I'm restless and wake up tired. What would help me?",
 
  analyzing_es: 'Analizando radiografía…',
  analyzing_en: 'Analyzing X-ray…',
  normal_es: 'Sin hallazgos significativos',
  normal_en: 'No significant findings',
  normal_sub_es: 'La radiografía no muestra anomalías detectables. Consulta a tu médico para una evaluación completa.',
  normal_sub_en: 'The X-ray shows no detectable anomalies. Consult your doctor for a full evaluation.',
  abnormal_es: 'Posibles hallazgos detectados',
  abnormal_en: 'Possible findings detected',
  abnormal_sub_es: 'Se detectaron patrones que merecen atención médica. Consulta a un especialista.',
  abnormal_sub_en: 'Patterns were detected that warrant medical attention. Consult a specialist.',
  disclaimer_es: '⚠️ Este análisis es orientativo. No reemplaza un diagnóstico médico profesional.',
  disclaimer_en: '⚠️ This analysis is for guidance only. It does not replace a professional medical diagnosis.',
};
 
function t(key){ return T[`${key}_${lang}`] || T[`${key}_es`] || ''; }
 
/* ══════════════════════════════════════════════════════════════
   LANGUAGE
══════════════════════════════════════════════════════════════ */
function setLang(l){
  lang = l;
  document.documentElement.lang = l;
  document.getElementById('btn-es').classList.toggle('active', l==='es');
  document.getElementById('btn-en').classList.toggle('active', l==='en');
 
  // Update all [data-es] / [data-en] elements
  document.querySelectorAll('[data-es]').forEach(el=>{
    if(el.hasAttribute('data-placeholder-es')){
      el.placeholder = el.getAttribute(`data-placeholder-${l}`);
    } else {
      el.textContent = el.getAttribute(`data-${l}`);
    }
  });
  document.querySelectorAll('[data-placeholder-es]').forEach(el=>{
    el.placeholder = el.getAttribute(`data-placeholder-${l}`);
  });
}
 
/* ══════════════════════════════════════════════════════════════
   TABS
══════════════════════════════════════════════════════════════ */
function switchTab(tab){
  document.querySelectorAll('.section').forEach(s=>s.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(b=>b.classList.remove('active'));
  document.getElementById(`section-${tab}`).classList.add('active');
  document.getElementById(`tab-${tab}`).classList.add('active');
}
 
/* ══════════════════════════════════════════════════════════════
   CHAT
══════════════════════════════════════════════════════════════ */
function formatMarkdown(text){
  return text
    .replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>')
    .replace(/\*(.*?)\*/g,'<em>$1</em>')
    .replace(/^•\s?/gm,'• ')
    .replace(/\n/g,'<br>');
}
 
function addMessage(role, content, isTyping=false){
  const box   = document.getElementById('chat-messages');
  const wrap  = document.createElement('div');
  wrap.className = `msg ${role}`;
  wrap.innerHTML = `
    <div class="msg-avatar">${role==='user'?'👤':'🩺'}</div>
    <div class="msg-bubble" id="bubble-${Date.now()}">
      ${isTyping
        ? '<div class="typing-dots"><span></span><span></span><span></span></div>'
        : formatMarkdown(content)}
    </div>`;
  box.appendChild(wrap);
  box.scrollTop = box.scrollHeight;
  return wrap.querySelector('.msg-bubble');
}
 
async function sendMessage(){
  if(sending) return;
  const input  = document.getElementById('msg-input');
  const budget = document.getElementById('budget-input').value.trim();
  const text   = input.value.trim();
  if(!text) return;
 
  sending = true;
  document.getElementById('send-btn').disabled = true;
  input.value = '';
  input.style.height = '52px';
 
  addMessage('user', text);
  chatHistory.push({role:'user', content:text});
 
  // Typing indicator
  const typingBubble = addMessage('nova','',true);
 
  try {
    const res = await fetch(`${API}/api/chat`,{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({
        message: text,
        history: chatHistory.slice(0,-1),
        language: lang,
        budget: budget||null,
      }),
    });
    const data = await res.json();
    if(!res.ok) throw new Error(data.detail||'Error');
 
    typingBubble.innerHTML = formatMarkdown(data.response);
    chatHistory.push({role:'model', content:data.response});
  } catch(err){
    typingBubble.innerHTML = `<span style="color:var(--red)">⚠️ ${err.message}</span>`;
  }
 
  sending = false;
  document.getElementById('send-btn').disabled = false;
  document.getElementById('chat-messages').scrollTop = 999999;
}
 
function handleKey(e){
  if(e.key==='Enter' && !e.shiftKey){
    e.preventDefault();
    sendMessage();
  }
  // Auto-resize textarea
  const ta = document.getElementById('msg-input');
  ta.style.height='52px';
  ta.style.height=Math.min(ta.scrollHeight,140)+'px';
}
 
function quickAsk(key){
  document.getElementById('msg-input').value = t(key);
  sendMessage();
}
 
/* ══════════════════════════════════════════════════════════════
   X-RAY UPLOAD
══════════════════════════════════════════════════════════════ */
function triggerUpload(){ document.getElementById('file-input').click(); }
 
function onDragOver(e){
  e.preventDefault();
  document.getElementById('upload-zone').classList.add('drag-over');
}
function onDragLeave(e){
  document.getElementById('upload-zone').classList.remove('drag-over');
}
function onDrop(e){
  e.preventDefault();
  document.getElementById('upload-zone').classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if(file) loadFile(file);
}
function onFileSelected(e){
  const file = e.target.files[0];
  if(file) loadFile(file);
}
 
function loadFile(file){
  if(!file.type.match(/image\/(jpeg|png)/)){
    showToast('⚠️ Solo JPG y PNG / Only JPG and PNG');
    return;
  }
  currentFile = file;
  const reader = new FileReader();
  reader.onload = ev => {
    const preview = document.getElementById('xray-preview');
    preview.src   = ev.target.result;
    preview.style.display = 'block';
    document.getElementById('upload-placeholder').style.display = 'none';
    document.getElementById('upload-zone').classList.add('has-image');
    document.getElementById('upload-controls').style.display = 'flex';
  };
  reader.readAsDataURL(file);
}
 
function resetXray(){
  currentFile = null;
  document.getElementById('xray-preview').style.display='none';
  document.getElementById('xray-preview').src='';
  document.getElementById('upload-placeholder').style.display='';
  document.getElementById('upload-zone').classList.remove('has-image');
  document.getElementById('upload-controls').style.display='none';
  document.getElementById('file-input').value='';
  document.getElementById('results-empty').style.display='';
  document.getElementById('results-content').style.display='none';
}
 
async function analyzeXray(){
  if(!currentFile){ showToast('⚠️ Selecciona una imagen primero'); return; }
 
  const btn = document.getElementById('analyze-btn');
  btn.disabled = true;
  btn.innerHTML = `<div class="spinner" style="width:20px;height:20px;border-width:2px;"></div> <span>${t('analyzing')}</span>`;
 
  document.getElementById('results-empty').innerHTML =
    `<div class="spinner"></div><p style="color:var(--txt-3);margin-top:12px;font-size:14px;">${t('analyzing')}</p>`;
 
  try {
    const form = new FormData();
    form.append('file', currentFile);
 
    const res  = await fetch(`${API}/api/analyze-xray`,{method:'POST',body:form});
    const data = await res.json();
    if(!res.ok) throw new Error(data.detail||'Error en el análisis');
 
    renderResults(data);
  } catch(err){
    document.getElementById('results-empty').innerHTML =
      `<div class="results-empty-icon">❌</div><div class="results-empty-text" style="color:var(--red)">${err.message}</div>`;
  }
 
  btn.disabled = false;
  btn.innerHTML = `<span>🔍</span> <span>${lang==='es'?'Analizar Radiografía':'Analyze X-Ray'}</span>`;
}
 
function renderResults(data){
  document.getElementById('results-empty').style.display='none';
  const el = document.getElementById('results-content');
  el.style.display='block';
 
  const top8 = (data.findings||[]).slice(0,8);
  const isNormal = data.is_normal;
 
  el.innerHTML = `
    <div class="verdict-banner ${isNormal?'normal':'abnormal'}">
      <div class="verdict-icon">${isNormal?'✅':'⚠️'}</div>
      <div class="verdict-text">
        <h3>${isNormal?t('normal'):t('abnormal')}</h3>
        <p>${isNormal?t('normal_sub'):t('abnormal_sub')}</p>
      </div>
    </div>
 
    <div class="findings-title">${lang==='es'?'Condiciones analizadas (top 8)':'Analyzed conditions (top 8)'}</div>
 
    ${top8.map(f=>`
      <div class="finding-item">
        <div class="finding-header">
          <div class="finding-name">
            <div class="finding-dot ${f.severity}"></div>
            ${lang==='es' ? f.condition_es : f.condition}
          </div>
          <div class="finding-pct ${f.severity}">${f.confidence}%</div>
        </div>
        <div class="finding-bar-track">
          <div class="finding-bar ${f.severity}" data-w="${f.confidence}"></div>
        </div>
        <div class="finding-desc">${lang==='es'?f.description_es:f.description_en}</div>
      </div>
    `).join('')}
 
    <p style="font-size:12px;color:var(--txt-3);border-top:1px solid var(--border);padding-top:14px;">
      ${t('disclaimer')}
    </p>`;
 
  // Animate bars
  requestAnimationFrame(()=>{
    el.querySelectorAll('.finding-bar').forEach(bar=>{
      setTimeout(()=>{bar.style.width=bar.dataset.w+'%';},50);
    });
  });
}
 
/* ══════════════════════════════════════════════════════════════
   TOAST
══════════════════════════════════════════════════════════════ */
function showToast(msg, duration=3000){
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(()=>t.classList.remove('show'), duration);
}
 
/* ══════════════════════════════════════════════════════════════
   INIT
══════════════════════════════════════════════════════════════ */
window.addEventListener('DOMContentLoaded',()=>{
  // Welcome message
  addMessage('nova', t('welcome'));
  // Apply initial lang
  setLang('es');
});