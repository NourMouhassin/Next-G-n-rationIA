"""Pair B only: reproduce C09 and its row-preserving delta, without network calls."""
import csv
import hashlib
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path
import td1

ROOT = Path(__file__).resolve().parent
OUT = ROOT/'evidence/td2-binome-B'
SQL = ROOT/'sql/td2-binome-B'
MODELS = [f"{m['gate']}:{m['identifiant_exact']}" for m in td1.CONFIG['modeles']]
QWEN = 'groq:qwen/qwen3.8-27b'
COHERE = 'openrouter:cohere/north-mini-code:free'
PANEL = ['groq:openai/gpt-oss-120b', COHERE, QWEN]

def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def query(sql, max_rows=10000):
    result = td1.s.sandbox_sqlite.execute_query(ROOT/'data/boutique.sqlite',sql,max_rows=max_rows)
    assert result['ok'] and not result['rejected'], result
    return result

def projection(sql):
    # Keep the entire original FROM/JOIN/WHERE, replacing only the aggregate SELECT.
    suffix=re.split(r'\bFROM\b',sql,maxsplit=1,flags=re.I)[1].rstrip().rstrip(';')
    return ('SELECT o.order_id, o.product_id, o.customer_id, o.date AS order_date, '
            'c.birth_date, o.quantity_product, p.price, '
            'o.quantity_product * p.price AS revenue_cents FROM '+suffix)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    SQL.mkdir(parents=True,exist_ok=True)
    protected=[ROOT/'traces-td1.csv',ROOT/'reference-td1.csv',ROOT/'data/boutique.sqlite',
               *sorted((ROOT/'data').glob('*.csv'))]
    before={str(p.relative_to(ROOT)):digest(p) for p in protected}
    rows=read_csv(ROOT/'traces-td1.csv')
    latest={}
    for index,row in enumerate(rows,1):
        if row['nature']!='real':
            continue
        key=row['cell_id']
        rank=(int(row['attempts']),row['date_utc'])
        if key not in latest or rank>latest[key][0]:
            latest[key]=(rank,row,index)
    assert len(latest)==100
    shared=[]
    for q in td1.QUESTIONS:
        groups={}
        for _,r,_ in latest.values():
            if r['case_id']==q['id'] and r['verdict']=='incorrect' and r['value']!='':
                groups.setdefault(r['value'],[]).append(r['cell_id'])
        shared.extend(dict(case_id=q['id'],value=int(v),cells=c) for v,c in groups.items() if len(c)>=2)
    selected={m:latest[f'{m}:C09'][1] for m in MODELS}
    ref=next(r for r in read_csv(ROOT/'reference-td1.csv') if r['case_id']=='C09')
    expected=int(ref['revenue_cents'])
    assert query(ref['sql'])['value']==expected==487980
    (SQL/'C09-reference.sql').write_text(ref['sql'],encoding='utf-8',newline='')
    queries={}
    for label,model in [('qwen',QWEN),('cohere',COHERE)]:
        raw=selected[model]['sql']
        (SQL/f'C09-{label}-original.sql').write_text(raw,encoding='utf-8',newline='')
        assert (SQL/f'C09-{label}-original.sql').read_text(encoding='utf-8')==raw
        assert query(raw)['value']==int(selected[model]['value'])==0
        queries[label]=raw
    ctes=['reference_lines AS (\n'+projection(ref['sql'])+'\n)']
    ctes += [label+'_lines AS (\n'+projection(sql)+'\n)' for label,sql in queries.items()]
    branches=[]
    for label in queries:
        for kind,left,right in [('omitted','reference_lines',label+'_lines'),('added',label+'_lines','reference_lines')]:
            branches.append(f"SELECT '{label}' AS faulty_model, '{kind}' AS difference, a.* FROM {left} a "
                f'WHERE NOT EXISTS (SELECT 1 FROM {right} b WHERE b.order_id=a.order_id AND b.product_id=a.product_id)')
    diagnostic='WITH '+',\n'.join(ctes)+'\n'+'\nUNION ALL\n'.join(branches)+'\nORDER BY faulty_model, difference, customer_id, order_id, product_id;\n'
    (SQL/'C09-delta.sql').write_text(diagnostic,encoding='utf-8')
    result=query(diagnostic)
    delta=[dict(zip(result['columns'],r)) for r in result['rows']]
    with (OUT/'C09-delta.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=result['columns'],lineterminator='\n'); w.writeheader(); w.writerows(delta)
    # Independent CSV arithmetic, Python dates and predicates: no SQL totals as inputs.
    prices={r['product_id']:int(r['price']) for r in read_csv(ROOT/'data/product.csv')}
    births={r['customer_id']:date.fromisoformat(r['birth_date']) for r in read_csv(ROOT/'data/customers.csv')}
    independent=[]
    ref_total=0
    faulty_totals={'qwen':0,'cohere':0}
    for r in read_csv(ROOT/'data/orders.csv'):
        b=births[r['customer_id']]; day=date.fromisoformat(r['date'][:10]); reference_day=date(2026,9,26)
        correct=b.replace(year=b.year+25)<=reference_day<b.replace(year=b.year+26)
        md=lambda d:(d.month,d.day)
        wrong={'qwen':day.year-b.year==25 and md(day)>=md(b) and md(day)<md(b.replace(year=b.year+26)),
               'cohere':b.year-int(md(b)>(9,26))==25}
        amount=int(r['quantity_product'])*prices[r['product_id']]
        if correct: ref_total+=amount
        for label,match in wrong.items():
            if match: faulty_totals[label]+=amount
            if correct!=match:
                independent.append((label,'omitted' if correct else 'added',r['order_id'],r['product_id'],r['customer_id'],amount))
    actual=[(r['faulty_model'],r['difference'],r['order_id'],r['product_id'],r['customer_id'],r['revenue_cents']) for r in delta]
    assert Counter(actual)==Counter(independent), 'SQL/CSV line-level mismatch'
    assert ref_total==expected
    totals={}
    for label in queries:
        own=[r for r in delta if r['faulty_model']==label]
        omitted=sum(r['revenue_cents'] for r in own if r['difference']=='omitted')
        added=sum(r['revenue_cents'] for r in own if r['difference']=='added')
        assert omitted-added==expected-faulty_totals[label]==expected
        totals[label]=dict(omitted_cents=omitted,added_cents=added,delta_cents=omitted-added,
            omitted_lines=sum(r['difference']=='omitted' for r in own),added_lines=sum(r['difference']=='added' for r in own),
            customers=len({r['customer_id'] for r in own}),csv_reference_cents=ref_total,csv_faulty_cents=faulty_totals[label],line_level_csv_match=True)
    votes={}
    voter=td1.s.Orchestrateur.__new__(td1.s.Orchestrateur)
    for label,panel,k in [('2_of_3',PANEL,2),('3_of_5',MODELS,3)]:
        proposals=[]
        for model in panel:
            r=selected[model]
            has_value=r['verdict'] in ('correct','incorrect') and r['value']!=''
            proposals.append(dict(provider=r['provider'],model_requested=r['model_requested'],value=int(r['value']) if has_value else None,verdict='executed' if has_value else 'error'))
        counts=Counter(p['value'] for p in proposals if p['verdict']=='executed')
        winner,n=counts.most_common(1)[0]
        manual=dict(consensus=n>=k,value=winner if n>=k else None,votes=n,models=sorted(f"{p['provider']}:{p['model_requested']}" for p in proposals if p['value']==winner) if n>=k else [])
        check='pending: Pair A method raises NotImplementedError'
        try:
            implemented=voter.vote_k_sur_n(proposals,k)
        except NotImplementedError:
            pass
        else:
            normalized=dict(implemented,models=sorted(implemented['models']))
            assert normalized==manual,(normalized,manual)
            check='passed: Pair A vote_k_sur_n equals manual count'
        votes[label]=dict(panel=panel,k=k,n=len(panel),counts=dict(counts),manual=manual,agrees_with_reference=manual['value']==expected,pair_A_check=check)
    identities=[]
    for m,r in selected.items():
        original=ROOT/'runs'/('state-'+ 'ABCDE'[MODELS.index(m)]+'.jsonl')
        lines=[(i,json.loads(line)) for i,line in enumerate(original.read_text(encoding='utf-8').splitlines(),1) if line.strip()]
        number=next(i for i,x in lines if x['cell_id']==r['cell_id'] and int(x['attempts'])==int(r['attempts']))
        identities.append(dict(model=m,cell_id=r['cell_id'],attempt=int(r['attempts']),date_utc=r['date_utc'],
            source=f'{original.relative_to(ROOT).as_posix()}#L{number}',csv_record=latest[r['cell_id']][2],value_cents=int(r['value']) if r['value'] else None,verdict=r['verdict'],prompt_sha256=r['prompt_sha256']))
    assert before=={str(p.relative_to(ROOT)):digest(p) for p in protected}
    evidence=dict(nature='real TD1 batch; offline diagnostic',final_cells=len(latest),real_attempts=sum(r['nature']=='real' for r in rows),reference_cents=expected,
        proposals=identities,shared_wrong_cases=shared,delta=totals,votes=votes,source_sha256=before,database_unchanged=True)
    (OUT/'C09-evidence.json').write_text(json.dumps(evidence,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(dict(reference_cents=expected,delta=totals,votes=votes,database_unchanged=True),indent=2))

if __name__=='__main__':
    main()
