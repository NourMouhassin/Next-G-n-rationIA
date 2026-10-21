"""Small TD1 driver: offline preparation, safe assigned batch, consolidation, pivot."""
import argparse
import csv
import importlib.util
import json
import os
import subprocess
import sys
import time
from dataclasses import fields
from decimal import Decimal
from pathlib import Path
import build_references as ref

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('td1_skeleton', ROOT/'skeleton-multi-llm-en.py')
s = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = s
spec.loader.exec_module(s)
CONFIG = json.loads((ROOT/'modeles-autorises.json').read_text(encoding='utf-8'))
QUESTIONS = json.loads((ROOT/'questions-td1.json').read_text(encoding='utf-8'))['questions']
SCHEMA = (ROOT/'schema.sql').read_text(encoding='utf-8')
COMPARISON = ['case_id','model_id','trace_file','cell_id','nature','status','value_cents','reference_cents','explanation']
SUMMARY = ['provider','model_id','public_index','index_date','index_source','paid_route_same_model','input_usd_per_million','output_usd_per_million','price_date','price_source','access_used','period_results','age_results','product_results','combined_results','trace_files','limits']

def save_json(path, value):
    (ROOT/path).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def prompts():
    records = []
    text = '# TD1 experimental prompts\n\nPrepared verbatim from the runner. No real call yet unless supported by runs/*.jsonl.\n\n'
    text += '## System message\n\n```text\n'+s.SYSTEM_PROMPT+'\n```\n\n## User template\n\n```text\n'+s.USER_PROMPT_TEMPLATE+'\n```\n'
    for q in QUESTIONS:
        system, user, digest = s.build_prompt(SCHEMA, q['question'])
        records.append(dict(case_id=q['id'], system=system, user=user, prompt_sha256=digest))
        text += f"\n## {q['id']} — {digest}\n\n```text\n{user}\n```\n"
    (ROOT/'prompts-en.md').write_text(text, encoding='utf-8')
    save_json('evidence/prompts.json', records)

def load_attempts():
    references = s.load_references(ROOT/'reference-td1.csv')
    questions = {q['id']: q for q in QUESTIONS}
    models = {f"{m['gate']}:{m['identifiant_exact']}" for m in CONFIG['modeles']}
    attempts, seen = [], {}
    for path in sorted((ROOT/'runs').glob('state-*.jsonl')):
        for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            if not line.strip():
                continue
            row = json.loads(line)
            model = f"{row['provider']}:{row['model_requested']}"
            case = row['case_id']
            assert model in models and case in questions, (path, number, 'unknown model/case')
            assert row['cell_id'] == f'{model}:{case}'
            assert row['nature'] in ('real','replay','simulation','simulated')
            assert row['prompt_sha256'] == s.build_prompt(SCHEMA, questions[case]['question'])[2], 'Different experiment prompt'
            assert str(row['reference']) == str(references[case]), 'Different reference'
            assert int(row['attempts']) in (1,2)
            key = (row['nature'], row['cell_id'], int(row['attempts']))
            if key in seen:
                assert seen[key] == row, f'Conflicting attempt {key}; keep separate experiments'
                continue
            seen[key] = row
            attempts.append((row, f'{path.relative_to(ROOT).as_posix()}#L{number}'))
    attempts.sort(key=lambda item: (item[0]['date_utc'], item[0]['cell_id'], int(item[0]['attempts'])))
    for row, _ in attempts:
        if int(row['attempts']) == 2 and row['nature'] == 'real':
            assert (row['nature'],row['cell_id'],1) in seen, 'Missing first attempt'
    return attempts

def explanation(row):
    status = row['verdict']
    if status == 'correct':
        return 'Read-only SQL result equals independently checked reference.'
    if status == 'access_error':
        return f"API access failure HTTP {row['http_status']}; SQL not evaluated. {row['error']}"
    if row.get('finish_reason') == 'length':
        return 'Provider reports length limit; inspect response_text and SQL. '+row['verdict_detail']
    if status in ('sql_invalid','sql_rejected'):
        return 'Sandbox/SQL evidence: '+row['verdict_detail']
    if status == 'incorrect':
        return 'Observed value differs; inspect SQL against reference. Specific semantic cause requires human review. '+row['verdict_detail']
    return 'No evaluated SQL: '+row['error']+' '+row['verdict_detail']

def consolidate():
    attempts = load_attempts()
    names = [f.name for f in fields(s.Trace)]
    ref.write_csv('traces-td1.csv', names, [{k:r.get(k,'') for k in names} for r,_ in attempts])
    (ROOT/'traces-td1.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False)+'\n' for r,_ in attempts), encoding='utf-8')
    latest = {}
    for row, source in attempts:
        key = (row['nature'], row['cell_id'])
        if key not in latest or int(row['attempts']) > int(latest[key][0]['attempts']):
            latest[key] = (row, source)
    refs = s.load_references(ROOT/'reference-td1.csv')
    comparison = []
    for model in CONFIG['modeles']:
        name = f"{model['gate']}:{model['identifiant_exact']}"
        for q in QUESTIONS:
            cell = f"{name}:{q['id']}"
            # Official comparison covers real experiment only. Other natures remain in raw traces.
            observed = latest.get(('real',cell))
            r = dict(case_id=q['id'], model_id=name, trace_file='', cell_id=cell, nature='', status='not_executed', value_cents='', reference_cents=refs[q['id']], explanation='No real attempt supplied; assignment, account quota and group turn must be confirmed before running.')
            if observed:
                row, source = observed
                r.update(trace_file=source, nature='real', status=row['verdict'], value_cents=row['value'], explanation=explanation(row)+f" Final attempt {row['attempts']}.")
            comparison.append(r)
    assert len(comparison)==100 and len({r['cell_id'] for r in comparison})==100
    ref.write_csv('model-question-comparison-en.csv', COMPARISON, comparison)
    summary(comparison)
    save_json('evidence/consolidation.json', {'attempts':len(attempts), 'real_attempts':sum(r['nature']=='real' for r,_ in attempts), 'real_cells':sum(r['nature']=='real' for r in comparison), 'final_rows':len(comparison), 'natures_separated':True, 'duplicate_final_cells':0})
    print(f'Consolidated {len(attempts)} attempts; 100 final rows (unrun cells explicitly marked).')

def summary(comparison):
    portfolio = ref.read_csv('portefeuille-modeles-2026-09-28.csv')
    prices = json.loads((ROOT/'docs/paid-route-snapshot.json').read_text(encoding='utf-8'))
    rows = []
    family = lambda q: 'combined' if '+' in q['type'] else 'period' if q['type']=='period' else 'age' if 'age' in q['type'] else 'product'
    for m in CONFIG['modeles']:
        model, provider = m['identifiant_exact'], m['gate']
        candidates = [p for p in portfolio if p['identifiant_gate']==model and p['score_public']]
        paid = next((p for p in prices['models'] if p['id']==model.removesuffix(':free') and not p['id'].endswith(':free')), None)
        r = {k:'' for k in SUMMARY}
        r.update(provider=provider, model_id=model, public_index=candidates[0]['score_public'] if candidates else 'N/A: absent from supplied portfolio', index_date='2026-09-28', index_source='portefeuille-modeles-2026-09-28.csv (benchmark name not specified by source)', price_date=prices['retrieved_date'], price_source=prices['source']+' ; docs/paid-route-snapshot.json', access_used='Not executed; planned '+provider+(' Free plan' if provider=='groq' else ' :free, maximum input/output price 0'), trace_files='traces-td1.jsonl; runs/state-*.jsonl when supplied', limits='No general ranking. Disjoint families: period 6, age 5, product 4, combined 5. Public index is a dated course snapshot, not a local measurement.')
        if paid:
            r.update(paid_route_same_model='openrouter:'+paid['id'], input_usd_per_million=str(Decimal(paid['pricing']['prompt'])*1000000), output_usd_per_million=str(Decimal(paid['pricing']['completion'])*1000000))
        else:
            for key in ('paid_route_same_model','input_usd_per_million','output_usd_per_million'):
                r[key]='N/A: no exact paid model in retrieved public catalog'
        mine = [x for x in comparison if x['model_id']==f'{provider}:{model}']
        if any(x['nature']=='real' for x in mine):
            r['access_used'] = provider+(' Free plan (operator declaration)' if provider=='groq' else ' :free, zero-price cap')
        for f in ('period','age','product','combined'):
            ids = {q['id'] for q in QUESTIONS if family(q)==f}
            group = [x for x in mine if x['case_id'] in ids]
            attempted = [x for x in group if x['nature']=='real']
            correct = sum(x['status']=='correct' for x in attempted)
            access = sum(x['status']=='access_error' for x in attempted)
            r[f+'_results'] = f'{correct}/{len(attempted)} attempted correct; {access} access errors; {len(group)-len(attempted)} unrun; accuracy '+(f'{correct/len(attempted):.1%}' if attempted else 'N/A')
        rows.append(r)
    ref.write_csv('five-model-summary-en.csv', SUMMARY, rows)

def pivot():
    rows = ref.read_csv('model-question-comparison-en.csv')
    codes = {'correct':'OK','incorrect':'WR','sql_invalid':'SI','sql_rejected':'SR','access_error':'AE','not_executed':'--'}
    print('model'.ljust(55)+' '.join(q['id'] for q in QUESTIONS))
    for m in CONFIG['modeles']:
        name = f"{m['gate']}:{m['identifiant_exact']}"
        mine = {r['case_id']:r for r in rows if r['model_id']==name}
        print(name.ljust(55)+' '.join(codes.get(mine[q['id']]['status'],'??').center(3) for q in QUESTIONS))
    print('OK correct; WR wrong; SI invalid; SR rejected; AE access error; -- not executed (see explanation).')

def run(member):
    allocation = json.loads((ROOT/'allocation.json').read_text(encoding='utf-8'))
    selected = allocation['operators'][member]
    assert allocation['group_turn_confirmed'] is True, 'Group coordination required'
    assert allocation['distinct_personal_accounts_confirmed'] is True, 'C/E distinct OpenRouter accounts; A/B/D personal Groq accounts required'
    assert selected['confirmed'] is True and selected['member_name'], 'Confirm assigned operator'
    assert selected['free_plan_confirmed'] is True
    assert isinstance(selected['quota_remaining'], int) and selected['quota_remaining'] >= len(selected['cases'])+5, 'Confirm quota after controls, with five-call reserve; otherwise reallocate'
    model = next(m for m in CONFIG['budget_td1']['repartition'] if m['membre']==member)
    assert selected['cases'] and set(selected['cases']) <= {q['id'] for q in QUESTIONS}
    assert len(set(selected['cases']))==len(selected['cases'])
    key = s.KEY_ENV[model['gate']]
    assert os.environ.get(key,'').strip(), f'Missing {key} in this process; never read keys from files'
    assert selected['controls_already_used'] is not None
    state = ROOT/f'runs/state-{member}.jsonl'
    output = ROOT/f'runs/traces-{member}.csv'
    previous_count = len(s.TableTraces(state).lignes)
    # Five calls reserved for extra controls/retries; do not consume an unbounded retry budget.
    allowance = min(selected['quota_remaining'], len(selected['cases'])+5-previous_count)
    assert allowance > 0, 'Operator planning budget exhausted; coordinate reallocation'
    original_call = s.ClientHTTP._appeler
    calls = 0
    def bounded_call(client, system, user, case_id):
        nonlocal calls
        if calls >= allowance:
            raise SystemExit('Operator call budget reached; saved work retained. Coordinate before continuing.')
        calls += 1
        return original_call(client, system, user, case_id)
    lock = ROOT/'.run.lock'
    with lock.open('x', encoding='utf-8') as f:
        f.write('Local single operator lock. Other group machines require human coordination.\n')
    try:
        # No independent experiment is created on resume: same state and output names.
        s.ClientHTTP._appeler = bounded_call
        sys.argv = ['skeleton-multi-llm-en.py', '--run', '--models', f"{model['gate']}:{model['modele']}", '--cases', ','.join(selected['cases']), '--state', str(state), '--out', str(output)]
        time.sleep(3)  # Also preserve the interval at an operator handover.
        s.main()
    finally:
        s.ClientHTTP._appeler = original_call
        if state.exists():
            s.TableTraces(state).exporter_csv(output)
        lock.unlink()
        consolidate()

def prepare():
    result = subprocess.run([sys.executable, str(ROOT/'verify-data.py')], check=True, capture_output=True, text=True)
    (ROOT/'evidence/data-check.json').write_text(result.stdout, encoding='utf-8')
    ref.main()
    prompts()
    consolidate()
    pivot()

if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare','consolidate','pivot','run'])
    parser.add_argument('--member', choices=list('ABCDE'))
    args = parser.parse_args()
    if args.action=='run':
        if not args.member:
            parser.error('--member required')
        run(args.member)
    else:
        globals()[args.action]()
