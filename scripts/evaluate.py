"""Run the 20 saved local scenarios and write the actual results."""
import json
from pathlib import Path
import statistics
import sys
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from trip_planner.catalog import Catalog
from trip_planner.planner import plan

def evaluate():
    catalog=Catalog()
    cases=json.loads((ROOT/'tests/scenarios.json').read_text(encoding='utf-8'))
    outcomes=[]
    plans=[]
    for case in cases:
        output=plan(case['request'],catalog,provider='local')
        before=output['attempts'][0]['result']
        after=output['result']
        outcome={**case,'actual_status':after['status'],'matches_expected':after['status']==case['expected_status'],
            'initial_failed_checks':before['failure_count'],'final_failed_checks':after['failure_count'],
            'final_unknown_checks':after['unknown_count'],'attempts':len(output['attempts']),
            'elapsed_seconds':output['elapsed_seconds'],'admission_usd':after['total_admission_usd'],
            'walking_minutes':after['walking_minutes']}
        outcomes.append(outcome)
        plans.append({'scenario_id':case['id'],'output':output})
    summary={'run_at_utc':datetime.now(timezone.utc).isoformat(),'provider':'local','scenario_count':len(outcomes),
        'expected_outcomes_matched':sum(c['matches_expected'] for c in outcomes),
        'initial_plans_without_failed_checks':sum(c['initial_failed_checks']==0 for c in outcomes),
        'final_plans_without_failed_checks':sum(c['final_failed_checks']==0 for c in outcomes),
        'repaired_scenarios':sum(c['initial_failed_checks']>0 and c['final_failed_checks']==0 for c in outcomes),
        'fits_estimates':sum(c['actual_status']=='fits_estimates' for c in outcomes),
        'needs_change':sum(c['actual_status']=='needs_change' for c in outcomes),
        'needs_confirmation':sum(c['actual_status']=='needs_confirmation' for c in outcomes),
        'median_seconds':round(statistics.median(c['elapsed_seconds'] for c in outcomes),3),
        'max_seconds':max(c['elapsed_seconds'] for c in outcomes),
        'real_claude_calls':0,
        'interpretation':'These are saved regression cases for the local planner, not a user study or a Claude-versus-chatbot benchmark.',
        'outcomes':outcomes}
    (ROOT/'evidence').mkdir(exist_ok=True)
    (ROOT/'evidence/evaluation.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    (ROOT/'evidence/scenario_plans.json').write_text(json.dumps(plans,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='outcomes'},indent=2))
    for c in outcomes:
        print(('PASS' if c['matches_expected'] else 'FAIL'),c['id'],c['actual_status'])
    return all(c['matches_expected'] for c in outcomes)

if __name__=='__main__':
    raise SystemExit(0 if evaluate() else 1)
