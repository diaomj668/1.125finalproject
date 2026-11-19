"""Build an offline replay from actual evaluation outputs, without an API call."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
saved=json.loads((ROOT/'evidence/scenario_plans.json').read_text(encoding='utf-8'))
ids=['saturday_closures','saturday_free','old_nature_records']
selected={x['scenario_id']:x['output'] for x in saved if x['scenario_id'] in ids}
app=(ROOT/'web/app.js').read_text(encoding='utf-8')
helpers=app[app.index('const money'):app.index("fetch('/api/config')")]
render=app[app.index('function render(plan)'):app.index('function showExclusions')]
page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Midpoint demo replay</title><link rel="stylesheet" href="../web/style.css"></head><body>
<header><a class="brand" href="../README.md"><span class="brandmark">M</span> Massachusetts Trip Planner</a><span class="version">Mingjiao Diao</span></header><main>
<section class="hero"><div><p class="eyebrow">MIDPOINT CHECK-IN</p><h1>A draft, a check,<br>and a revised day.</h1><p>Three saved runs from the local planner. This page replays the results without a server or an API key. It does not generate a new itinerary.</p><div class="hero-tags"><span>Recorded November 13, 2026</span><span>Local planner · no LLM call</span></div></div><figure><img src="../web/boston.jpg" alt="Illustrative Boston waterfront view"><figcaption>Massachusetts Trip Planner · Cambridge pilot</figcaption></figure></section>
<div class="workspace"><aside class="input-panel"><div class="panel-heading"><span class="step">01</span><h2>Saved examples</h2></div><div class="examples" style="margin:0;border:0;padding:0"><button data-case="saturday_closures">Saturday closures</button><button data-case="saturday_free">Saturday with a $0 budget</button><button data-case="old_nature_records">Missing facts</button></div><div id="request-summary"></div><p class="field-note">These are saved outputs from evidence/scenario_plans.json. Run python run.py to build your own day.</p><p class="field-note">The five checked museums use a November 13, 2026 snapshot. Other records are historical.</p></aside><section class="output-panel"><div class="panel-heading"><span class="step">02</span><h2>Plan and checks</h2></div><div id="results"></div></section></div>
<section class="scope-note"><h2>What remains</h2><p>The local checks and revisions have been tested. The Claude prompt was revised and matched all three saved live cases in three repeated runs. Those cases were used to tune it, so the next step is to test it on other saved requests. Then compare with a plain chatbot and check walking estimates against street routes. No cloud deployment is needed to run the prototype.</p></section></main><footer><span>Mingjiao Diao · 1.125 Agentic Engineering</span><span>Saved midpoint demonstration</span></footer><script>'''
payload=json.dumps(selected,ensure_ascii=False).replace('<','\\u003c')
script='const saved='+payload+';const resultArea=document.querySelector("#results");let lastPlan=null;let busy=false;let excluded=[];\n'+helpers+render+'''
function showCase(id){lastPlan=saved[id];render(lastPlan);document.querySelectorAll('.replace').forEach(b=>b.remove());const q=lastPlan.request;document.querySelector('#request-summary').innerHTML=`<h3>${esc(q.date)}</h3><p>${esc(q.start)}–${esc(q.end)}<br>${q.stop_count} stops · ${q.adults} adult<br>${money(q.budget)} admission budget<br>${q.max_walk_minutes} min walking limit</p><p class="field-note">Interests: ${esc(q.interests.join(', '))}<br>Records: ${esc(q.source_mode)}</p>`;}
document.querySelectorAll('[data-case]').forEach(b=>b.addEventListener('click',()=>showCase(b.dataset.case)));showCase('saturday_closures');
'''
(ROOT/'docs/demo.html').write_text(page+script+'</script></body></html>',encoding='utf-8')
print('Created docs/demo.html from three saved evaluation runs.')
