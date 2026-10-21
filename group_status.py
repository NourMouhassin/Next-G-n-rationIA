"""Derived group follow-up and measured statistics; offline only."""
import csv
import json
import statistics
from pathlib import Path
import td1
import receive_batch

def main():
    attempts=td1.load_attempts()
    comparison=td1.ref.read_csv('model-question-comparison-en.csv')
    allocation=json.loads((td1.ROOT/'allocation.json').read_text(encoding='utf-8'))
    tracking=[]
    metrics=[]
    receipts=[]
    for member,m in zip('ABCDE',td1.CONFIG['modeles']):
        model=f"{m['gate']}:{m['identifiant_exact']}"
        original=td1.ROOT/f'runs/state-{member}.jsonl'
        final=[r for r in comparison if r['model_id']==model]
        rows=[r for r,_ in attempts if f"{r['provider']}:{r['model_requested']}"==model and r['nature']=='real']
        if original.exists():
            receipts.append(receive_batch.inspect_batch(member,td1.ROOT/'runs'))
        counts={status:sum(r['status']==status for r in final) for status in ('correct','incorrect','sql_invalid','sql_rejected','access_error','not_executed')}
        metric=dict(member=member,model=model,attempts=len(rows),attempted_cells=sum(r['nature']=='real' for r in final),**counts)
        metric['correct_per_20']=f"{counts['correct']}/20"
        for field in ('latency_ms','tokens_prompt','tokens_completion','tokens_reasoning','cost_native'):
            values=[float(r[field]) for r in rows if r.get(field) not in ('',None)]
            metric[field]={'observed':len(values),'missing':len(rows)-len(values),'sum':sum(values) if values else None,'mean':statistics.mean(values) if values else None,'median':statistics.median(values) if values else None}
        metrics.append(metric)
        operator=allocation['operators'][member]
        tracking.append(dict(member_name=operator['member_name'],role=member,model=model,
            completed_cells=sum(r['status'] in ('correct','incorrect','sql_invalid','sql_rejected') for r in final),
            received_files=f'runs/state-{member}.jsonl; runs/traces-{member}.csv' if original.exists() else '',
            checks='CSV/JSONL; SHA256; prompts; references; SQL replay' if original.exists() else '',
            github='PR #1 reviewed; files imported on G, PR not merged' if member=='E' else 'origin/main commit 196005d',
            missing='F human cross-check; protocol incident clarification'+(' ; operator identity/quotas/account evidence' if not operator['member_name'] else ' ; E declarations supplied by PR, not independently verified')))
    tracking.extend([
        dict(member_name='',role='F',model='',completed_cells='',received_files='',checks='',github='No F evidence received',missing='Named human review of C01-C20 and actual contribution'),
        dict(member_name='',role='G',model='',completed_cells='',received_files='A-E',checks='Consolidation and offline checks',github='td1/role-G',missing='Name; final sign-off after F and incident clarification')])
    td1.ref.write_csv('reports/group-tracking.csv',list(tracking[0]),tracking)
    incident_rows=[]
    for p in (td1.ROOT/'runs/failed-access').glob('*.jsonl'):
        incident_rows.extend(json.loads(line) for line in p.read_text(encoding='utf-8').splitlines() if line.strip())
    td1.save_json('evidence/group-audit.json',{'received':receipts,'main_experiment_attempts':len(attempts),'archived_incident_attempts':len(incident_rows),'all_recorded_attempts':len(attempts)+len(incident_rows),'final_cells':len(comparison),'human_review_F':'pending','metadata_caution':'Operator declarations are not independently verified; missing quotas stay unknown.'})
    td1.save_json('evidence/model-statistics.json',metrics)
    lines=['# Observed batch statistics','', 'Generated from original attempts. Metrics count every main-experiment attempt, including retries; missing values are excluded, never replaced by zero. The 40 archived access incidents are separate experiments, not extra votes or replacements.','', '| Lot | Attempts | Cells attempted | Correct / 20 | Wrong | Invalid SQL | No evaluated SQL |', '|---|---:|---:|---:|---:|---:|---:|']
    for r in metrics:
        lines.append(f"| {r['member']} | {r['attempts']} | {r['attempted_cells']} | {r['correct_per_20']} | {r['incorrect']} | {r['sql_invalid']+r['sql_rejected']} | {r['access_error']+r['not_executed']} |")
    lines+=['','Detailed metric coverage, means, medians and totals: [model-statistics.json](../evidence/model-statistics.json). Family counts: [five-model-summary-en.csv](../five-model-summary-en.csv).', '', '| Lot | Median latency ms (observed/attempts) | Input tokens total (observed/attempts) | Output tokens total (observed/attempts) | Native cost total (observed/attempts) |','|---|---|---|---|---|']
    for r in metrics:
        cells=[]
        for key,agg in [('latency_ms','median'),('tokens_prompt','sum'),('tokens_completion','sum'),('cost_native','sum')]:
            x=r[key]; value='N/A' if x[agg] is None else f'{x[agg]:g}'
            cells.append(f"{value} ({x['observed']}/{r['attempts']})")
        lines.append('| '+r['member']+' | '+' | '.join(cells)+' |')
    (td1.ROOT/'reports/observed-results.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f"Group: {len(attempts)} main attempts; {len(incident_rows)} archived incidents; F review pending.")

if __name__=='__main__':
    main()
