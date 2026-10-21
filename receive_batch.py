"""Offline import of one original operator pair. Never executes an API call."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch
import td1

def inspect_batch(member, source):
    state=source/f'state-{member}.jsonl'
    exported=source/f'traces-{member}.csv'
    records=[json.loads(x) for x in state.read_text(encoding='utf-8-sig').splitlines() if x.strip()]
    with exported.open(encoding='utf-8-sig',newline='') as f:
        csv_rows=list(csv.DictReader(f))
    if not records or len(records)!=len(csv_rows):
        raise ValueError('Empty lot or CSV/JSONL attempt count mismatch')
    assignment=next(x for x in td1.CONFIG['budget_td1']['repartition'] if x['membre']==member)
    for row, flat in zip(records,csv_rows):
        if row['provider']!=assignment['gate'] or row['model_requested']!=assignment['modele']:
            raise ValueError('Operator/model mismatch')
        if row['nature']!='real':
            raise ValueError('Operator lot must contain real attempts; isolate replay/simulation')
        if not set(row).issubset(flat):
            raise ValueError('CSV omits JSONL fields')
        for key,value in row.items():
            if flat[key] != ('' if value is None else str(value)):
                raise ValueError(f'CSV/JSONL mismatch: {row["cell_id"]}, {key}')
        if str(row['http_status'])=='200' and not row['error']:
            judged=td1.s.judge(td1.ROOT/'data/boutique.sqlite',row['sql'],row['reference'])
            if judged['verdict']!=row['verdict'] or judged['value']!=str(row['value']):
                raise ValueError(f'Local SQL judgement differs: {row["cell_id"]}')
    # Exercise the actual merger, including conflicts with already imported originals.
    with tempfile.TemporaryDirectory() as temporary:
        root=Path(temporary)
        (root/'runs').mkdir()
        shutil.copy2(td1.ROOT/'reference-td1.csv',root/'reference-td1.csv')
        for path in (td1.ROOT/'runs').glob('state-*.jsonl'):
            shutil.copy2(path,root/'runs'/path.name)
        shutil.copy2(state,root/'runs'/f'state-incoming-{member}.jsonl')
        with patch.object(td1,'ROOT',root):
            td1.load_attempts()
    return {'member':member,'attempts':len(records),'cells':len({r['cell_id'] for r in records}),
            'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (state,exported)},
            'checks':['CSV/JSONL equality','assigned model','real nature','prompt/reference','duplicate conflicts','local SQL judgement']}

def receive(member,source,origin,accept=False):
    report=inspect_batch(member,source)
    report['origin']=origin
    if accept:
        for filename in report['sha256']:
            dest=td1.ROOT/'runs'/filename
            if dest.exists() and dest.read_bytes()!=(source/filename).read_bytes():
                raise ValueError('Existing original differs; inspect and archive explicitly before replacement: '+filename)
        archive=td1.ROOT/'runs'/'received'/member
        archive.mkdir(parents=True,exist_ok=True)
        for filename in report['sha256']:
            dest=archive/filename
            if dest.exists() and dest.read_bytes()!=(source/filename).read_bytes():
                raise ValueError('Archived original differs: '+filename)
        for filename in report['sha256']:
            shutil.copy2(source/filename,archive/filename)
            shutil.copy2(source/filename,td1.ROOT/'runs'/filename)
        (archive/'receipt.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        td1.consolidate()
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--member',required=True,choices=list('ABCDE'))
    parser.add_argument('--source',type=Path,required=True,help='Folder containing the original JSONL and CSV')
    parser.add_argument('--origin',required=True,help='Branch/PR/commit or sender-provided provenance')
    parser.add_argument('--accept',action='store_true',help='Preserve originals and consolidate after validation')
    args=parser.parse_args()
    print(json.dumps(receive(args.member,args.source,args.origin,args.accept),indent=2))
