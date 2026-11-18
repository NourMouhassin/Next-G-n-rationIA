#!/usr/bin/env python3
"""ESILV TD2 — Pair C. Offline routing simulation derived from THIS team's TD1 traces.

Use from repository root (Python 3.10+, standard library only):
    python td2/binome-C/atelier-routage-adapte.py --table
    python td2/binome-C/atelier-routage-adapte.py
    python td2/binome-C/atelier-routage-adapte.py --scenario deferrable
    python td2/binome-C/atelier-routage-adapte.py --extra
    python td2/binome-C/atelier-routage-adapte.py --check-rates

This is a decision-policy simulator; it does not call any model and does NOT execute
or certify the reference checks it recommends. The seven scenarios have simulated
availability, prices from a DATED Oct-2026 snapshot, and an illustrative token
budget. Outcomes should not be interpreted as current provider availability.
"""
from __future__ import annotations
import argparse
import csv
import json
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
POLICY_PATH = HERE / 'policy.json'
VALID_STATUSES = {'correct', 'incorrect', 'not_executed', 'sql_invalid', 'sql_rejected', 'access_error', 'unscored'}


def load_inputs(root: Path = ROOT):
    policy = json.loads(POLICY_PATH.read_text(encoding='utf-8'))
    config = json.loads((root / 'modeles-autorises.json').read_text(encoding='utf-8'))
    catalog = json.loads((root / 'docs' / 'paid-route-snapshot.json').read_text(encoding='utf-8'))
    models = {}
    for item in config['modeles']:
        provider, name = item['gate'], item['identifiant_exact']
        key = provider + ':' + name
        if key in models:
            raise ValueError('Duplicate model in configuration: '+key)
        models[key] = {'provider': provider, 'name': name}
    if len(models) != 5:
        raise ValueError('Expected exactly five configured TD1 models, got '+str(len(models)))
    with (root / 'model-question-comparison-en.csv').open(encoding='utf-8-sig', newline='') as handle:
        rows = list(csv.DictReader(handle))
    statuses = {}
    for row in rows:
        key = (row['model_id'], row['case_id'])
        if key in statuses:
            raise ValueError('Duplicate TD1 final cell: '+str(key))
        if row['status'] not in VALID_STATUSES:
            raise ValueError('Unrecognized status: '+row['status'])
        statuses[key] = row['status']
    families = policy['families']
    unique_cases = [case for f in families.values() for case in f['cases']]
    if len(unique_cases) != 20 or set(unique_cases) != {f'C{i:02d}' for i in range(1,21)}:
        raise ValueError('Expected all twenty distinct reference questions in policy.json')
    if len(statuses) != 100 or set(statuses) != {(model, case) for model in models for case in unique_cases}:
        raise ValueError('Expected 5 x 20 real final TD1 cells')
    for family, meta in families.items():
        if set(meta['preferred_models']) != set(models):
            raise ValueError(f'Bad preference list in {family}')
    rates = {}
    for family, meta in families.items():
        cases = meta['cases']
        for model in models:
            failures = [case for case in cases if statuses[(model, case)] != 'correct']
            rates[(family, model)] = {'correct': len(cases)-len(failures),
                                      'count': len(cases), 'failures': failures}
    return policy, models, catalog, rates


def paid_cost(catalog: dict, model_name: str, token_envelope: dict) -> float | None:
    """Paid exact-model route only, with a dated price; no invented equivalent."""
    if model_name.endswith(':free'):
        return None
    entry = next((x for x in catalog['models'] if x['id'] == model_name), None)
    if entry is None:
        return None
    price = entry['pricing']
    try:
        cash = (Decimal(price['prompt']) * Decimal(token_envelope['input']) +
                Decimal(price['completion']) * Decimal(token_envelope['output']))
    except (KeyError, ValueError):
        return None
    if cash <= 0:
        return None
    return float(cash)


def make_resources(policy, models, catalog, rates):
    envelope = policy['token_envelope']
    resources = []
    for model, meta in models.items():
        eligible = [fam for fam in policy['families']
                    if rates[(fam, model)]['correct'] == rates[(fam, model)]['count']]
        resources.append({'id': model, 'model': model, 'access': 'free', 'available': True,
                          'cash': 0.0, 'allocation': 0.0, 'reset_minutes': None,
                          'families': eligible, 'source': 'real_td1_model; simulated_availability'})
        cost = paid_cost(catalog, meta['name'], envelope)
        if cost is not None:
            resources.append({'id': 'paid:'+model, 'model': model, 'access': 'tokens',
                              'available': True, 'cash': cost, 'allocation': cost,
                              'reset_minutes': None, 'families': eligible,
                              'source': 'dated_catalog_price; simulated_availability'})
    return resources


def checks_for(family, use):
    if use not in {'dashboard','customer','payout'}:
        raise ValueError('use must be dashboard/customer/payout')
    simple = family in {'F1_period', 'F3_product'}
    if use == 'payout':
        return 'independent read-only reference SQL + human approval before payout'
    if use == 'customer':
        if simple:
            return '2-of-3 distinct-family quorum; if unavailable: deterministic SQL or abstain'
        return 'independent deterministic reference SQL; reject mismatch (majority not sufficient)'
    if simple:
        return 'none for low-impact dashboard; log SQL and result (TD1 simple families only)'
    return 'deterministic read-only reference SQL before using age-dependent value'


def choose(request, resources, policy, rates):
    """Same order as the official kit: included -> wait -> paid -> abstain.

    Only models with 100% observed correctness in the *named TD1 family* qualify
    for the primary route. Model access or confidence is NOT inferred from size.
    An abstention, not an inaccurate substitute, is returned if no adequate route
    satisfies budget/deadline. Check descriptions are obligations, not executions.
    """
    family = request['family']
    if family not in policy['families']:
        return {'action':'abstain','resource':None,'cash':0,'checks':'human re-specification',
                'reason':f'{family}: unknown family; no eligibility evidence in TD1 C01-C20'}
    use = request['use']
    checks = checks_for(family, use)
    ordered = policy['families'][family]['preferred_models']
    order = {model:i for i,model in enumerate(ordered)}
    eligible = [r for r in resources if family in r['families']]
    def evidence(r):
        stat = rates[(family,r['model'])]
        return (f"{r['model']} {stat['correct']}/{stat['count']} correct for {family} "
                f"({', '.join(policy['families'][family]['cases'])}); "
                'small TD1 sample, not a general accuracy guarantee')
    included = [r for r in eligible if r['available'] and r['cash'] == 0]
    if included:
        # a free route is preferred to already-paid capacity; both are marginally zero cash.
        chosen = min(included, key=lambda r:(r['allocation'],order[r['model']],r['id']))
        return {'action':'run', 'resource':chosen['id'], 'cash':0,'checks':checks,
                'reason':'eligible included capacity; '+evidence(chosen)}
    waiting = [r for r in eligible if not r['available'] and r['cash'] == 0
               and r['reset_minutes'] is not None and 0 < r['reset_minutes'] <= request['deadline_minutes']]
    if waiting and request['can_wait']:
        chosen = min(waiting,key=lambda r:(r['reset_minutes'],r['allocation'],order[r['model']]))
        return {'action':'defer','resource':chosen['id'],'cash':0,'checks':checks,
                'wake_in_minutes':chosen['reset_minutes'],
                'reason':'free quota potentially refills before deadline; recheck on wake-up; '+evidence(chosen)}
    paid = [r for r in eligible if r['available'] and r['cash'] > 0 and r['cash'] <= request['budget']]
    if paid:
        chosen = min(paid,key=lambda r:(r['cash'],order[r['model']],r['id']))
        return {'action':'run','resource':chosen['id'],'cash':chosen['cash'],'checks':checks,
                'reason':'estimated paid exact-model route within simulated budget (catalog '+request.get('price_date','2026-10-21')+'); '+evidence(chosen)}
    return {'action':'abstain','resource':None,'cash':0,'checks':checks,
            'reason':f'no proven-on-{family} resource within budget and deadline (no unsupported downgrade)'}


def scenarios(resources):
    """The official kit's seven scenario intents, mapped to real TD1 families.

    Unlike the unchanged official original, the candidate resources are the team's
    actual five models (+ documented paid equivalents), not three fake models.
    All availabilities and quota reset times BELOW are synthetic.
    """
    base = {'family':'F1_period','use':'dashboard','can_wait':True,
            'deadline_minutes':120,'budget':0.30,'price_date':'2026-10-21'}
    exhausted = [dict(r,available=False,reset_minutes=60) if r['access']=='free' else dict(r)
                 for r in resources]
    return [
        ('simple', base, resources),
        ('complex',{**base,'family':'F4_combined'},resources),
        ('deferrable',{**base,'family':'F4_combined'},exhausted),
        ('urgent',{**base,'family':'F4_combined','can_wait':False,'deadline_minutes':5},exhausted),
        ('budget exhausted',{**base,'family':'F4_combined','can_wait':False,'budget':0},exhausted),
        ('high impact',{**base,'family':'F4_combined','use':'payout'},resources),
        ('unknown capability',{**base,'family':'F_unknown'},resources),
    ]


def extra_scenarios(resources):
    base = {'family':'F1_period','use':'customer','can_wait':True,
            'deadline_minutes':120,'budget':0.0005,'price_date':'2026-10-21'}
    down_cohere = [dict(r,available=False,reset_minutes=None) if r['id'].startswith('openrouter:cohere/')
                   else dict(r) for r in resources]
    exhausted_120b = [dict(r,available=False,reset_minutes=20) if r['id']=='groq:openai/gpt-oss-120b'
                      else dict(r) for r in resources]
    return [
        ('R2 provider unavailable',base,down_cohere),
        ('F2 age/date customer', {**base,'family':'F2_age_date'},resources),
        ('F2 age/date deferrable', {**base,'family':'F2_age_date'},exhausted_120b),
        ('F2b age at order payout', {**base,'family':'F2b_age_order','use':'payout'},resources),
    ]


def output_scenarios(selected, policy, rates):
    for name,request,resources in selected:
        yield {'scenario':name,'nature':'simulation','request':request,
               'result':choose(request,resources,policy,rates)}


def main(argv=None, root=ROOT):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scenario',help='Only named scenario from the 7 kit scenarios or extras')
    parser.add_argument('--extra',action='store_true',help='Include additional group-specific scenarios')
    parser.add_argument('--table',action='store_true',help='Print TD1 family rates as CSV')
    parser.add_argument('--check-rates',action='store_true',help='Validate 100 cells and counts')
    args=parser.parse_args(argv)
    policy,models,catalog,rates=load_inputs(root)
    if args.table:
        print('family,model,correct,total,failed_cases')
        for family in policy['families']:
            for model in models:
                s=rates[(family,model)]
                print(f"{family},{model},{s['correct']},{s['count']},{' '.join(s['failures'])}")
        return 0
    if args.check_rates:
        print(json.dumps({'status':'OK','models':len(models),'cases':20,'cells':100,
              'families':list(policy['families']),'price_snapshot':catalog.get('retrieved_date'),
              'source':'model-question-comparison-en.csv (read, not modified)'}))
        return 0
    resources = make_resources(policy,models,catalog,rates)
    selected=scenarios(resources)+(extra_scenarios(resources) if args.extra else [])
    if args.scenario:
        selected=[s for s in selected if s[0]==args.scenario]
        if not selected:
            parser.error('unknown scenario: '+args.scenario)
    for item in output_scenarios(selected,policy,rates):
        print(json.dumps(item,ensure_ascii=False))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
