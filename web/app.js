const form = document.querySelector('#trip-form');
const resultArea = document.querySelector('#results');
const errorBox = document.querySelector('#error');
let excluded = [];
let lastPlan = null;
let busy = false;
const money = value => value == null ? 'Unknown' : `$${Number(value).toFixed(0)}`;
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const label = value => value.replaceAll('_',' ');
const tag = value => `<span class="tag ${esc(value)}">${esc(value[0].toUpperCase()+value.slice(1))}</span>`;
const sourceLink = (url,index) => /^https?:\/\//.test(url) ? `<a href="${esc(url)}" target="_blank" rel="noreferrer">Source ${index+1} ↗</a>` : '';

fetch('/api/config').then(r => r.json()).then(c => {
  document.querySelector('#provider').textContent = c.provider === 'claude' ? 'Claude API planner' : 'Local planner · no LLM call';
}).catch(() => { document.querySelector('#provider').textContent = 'Server unavailable'; });

function requestValues() {
  const f = new FormData(form);
  return {date:f.get('date'), start:f.get('start'), end:f.get('end'), adults:Number(f.get('adults')),
    budget:Number(f.get('budget')), max_walk_minutes:Number(f.get('max_walk_minutes')), stop_count:Number(f.get('stop_count')),
    interests:f.getAll('interest'), source_mode:f.get('source_mode'), excluded_ids:excluded};
}

function render(plan) {
  const r = plan.result;
  const titles = {fits_estimates:'Fits the saved facts and walking estimates',needs_change:'This draft still needs changes',needs_confirmation:'Some details still need checking'};
  const descriptions = {fits_estimates:'No failed checks in this plan. Walking remains an estimate; verify the linked pages before going.',needs_change:'Do not treat this draft as ready. The failed checks below explain what needs to change.',needs_confirmation:'The schedule has no known clashes, but missing facts prevent a complete check.'};
  const first = plan.attempts[0].result;
  resultArea.innerHTML = `<div class="status ${esc(r.status)}"><h3>${titles[r.status]}</h3><p>${descriptions[r.status]}</p></div>
    <div class="stats"><div><b>${money(r.total_admission_usd)}</b><span>group admission</span></div><div><b>${r.walking_minutes} min</b><span>estimated walking</span></div><div><b>${r.stops.length}</b><span>planned stops</span></div></div>
    <div class="plan-actions"><p>${esc(plan.request.date)} · ${esc(plan.request.start)}–${esc(plan.request.end)}</p><button type="button" class="small-button" id="download">Save plan JSON ↓</button></div>
    <p class="field-note">${esc(plan.provider_label)} · ${plan.elapsed_seconds}s · facts checked ${esc(plan.snapshot_date)}</p>
    ${plan.attempts.length>1 ? `<div class="attempt-note"><strong>After one revision:</strong> ${first.failure_count} failed checks → ${r.failure_count}. Open “What changed” below to compare the two drafts.</div>` : ''}
    <div>${r.stops.map((s,i) => {
      const f=s.record.facts;
      const hours=f.hours_status==='unknown'?'Hours unknown':(!f.hours?.length?'Closed':f.hours.map(x=>x.join('–')).join(', '));
      return `${s.walk_before ? `<p class="walk">↓ About ${s.walk_before.minutes} min walking ${tag('estimated')}</p>` : ''}<article class="stop"><div class="stop-head"><span class="stop-number">${i+1}</span><div><h3>${esc(s.name)}</h3><p class="time">${esc(s.start)}–${esc(s.end)} · ${s.duration_minutes} min</p></div></div><p class="details">${tag(f.hours_status)} ${esc(hours)}<br>${tag(f.price_status)} ${money(s.charged_admission_usd)} added to group admission</p><p class="details">${esc(f.note)}</p><div class="source-links">${f.source_urls.map(sourceLink).join('')}</div><button type="button" class="small-button replace" data-id="${esc(s.place_id)}">Leave this stop out and replan</button></article>`;
    }).join('')}</div>
    <h3 class="section-title">How this plan was checked</h3><div class="legend"><span class="tag verified">Verified</span> Matches a dated source or exact request rule<br><span class="tag estimated">Estimated</span> Calculated with assumptions<br><span class="tag unknown">Unknown</span> Needs more information</div>
    <details open><summary>Check results · ${r.failure_count} failed / ${r.unknown_count} unknown</summary><div class="table-scroll"><table class="check-table"><thead><tr><th>Result</th><th>Evidence</th><th>Check</th></tr></thead><tbody>${r.checks.map(c=>`<tr><td>${tag(c.result)}</td><td>${tag(c.evidence)}</td><td><strong>${esc(label(c.rule))}</strong><small>${esc(c.message)}</small></td></tr>`).join('')}</tbody></table></div></details>
    <details><summary>What changed · draft, checks, revision</summary><ol class="trace">${plan.trace.map(t=>`<li><strong>${esc(t.step)}.</strong> ${esc(t.detail)}</li>`).join('')}</ol>${plan.attempts.map(a=>`<p class="details"><strong>Draft ${a.attempt+1}:</strong> ${a.result.failure_count} failed checks</p><ol class="trace">${a.draft.map(s=>`<li>${esc(s.start)} · ${esc(plan.candidates.find(c=>c.place_id===s.place_id)?.name||s.place_id)}</li>`).join('')}</ol>`).join('')}</details>
    <details><summary>Sources and assumptions</summary><p class="details">${esc(plan.walking_method)}</p><ul class="trace">${plan.limits.map(s=>`<li>${esc(s)}</li>`).join('')}</ul><p class="details">The wider dataset has 500 place records from 2021. This pilot retrieves Cambridge records only. Reviews are not used for taste ranking yet.</p></details>`;
  document.querySelector('#download').addEventListener('click',()=>{
    const blob=new Blob([JSON.stringify(lastPlan,null,2)],{type:'application/json'});
    const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=`cambridge-plan-${lastPlan.request.date}.json`;a.click();URL.revokeObjectURL(a.href);
  });
  resultArea.querySelectorAll('.replace').forEach(b=>b.addEventListener('click',()=>{
    if(busy)return;
    excluded=[...new Set([...excluded,b.dataset.id])];showExclusions();build();
  }));
}

function showExclusions(){
  const box=document.querySelector('#exclusions');box.hidden=excluded.length===0;
  box.innerHTML=`${excluded.length} stop(s) left out. <button type="button" class="small-button" id="restore">Restore all stops</button>`;
  box.querySelector('button').addEventListener('click',()=>{excluded=[];showExclusions();});
}

async function build(){
  if(busy||!form.reportValidity())return;
  busy=true;errorBox.hidden=true;
  const button=document.querySelector('#plan-button');button.disabled=true;button.textContent='Checking your day…';
  document.querySelector('#output').setAttribute('aria-busy','true');
  try{
    const response=await fetch('/api/plan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(requestValues())});
    const data=await response.json();
    if(!response.ok)throw new Error(data.error||'The planner could not finish.');
    lastPlan=data;render(data);document.querySelector('#empty').hidden=true;resultArea.hidden=false;
  }catch(e){errorBox.textContent=e.message||'The local server is unavailable.';errorBox.hidden=false;}
  finally{busy=false;button.disabled=false;button.innerHTML='Build and check my day <span>→</span>';document.querySelector('#output').setAttribute('aria-busy','false');}
}

form.addEventListener('submit',e=>{e.preventDefault();build();});
document.querySelectorAll('[data-example]').forEach(button=>button.addEventListener('click',()=>{
  if(busy)return;
  form.reset();excluded=[];showExclusions();
  const example=button.dataset.example;
  if(example==='free'){form.elements.date.value='2026-11-16';form.elements.budget.value=0;form.elements.stop_count.value='2';}
  if(example==='historical'){form.elements.date.value='2026-11-18';form.elements.source_mode.value='historical';form.elements.stop_count.value='2';form.querySelectorAll('[name=interest]').forEach(c=>c.checked=c.value==='nature');}
  build();
}));
