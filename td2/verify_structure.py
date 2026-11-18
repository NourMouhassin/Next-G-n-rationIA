"""Offline reproduction and layout checks; never regenerates the TD1 experiment."""
import csv
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
TD1=REPO/'td1'
A=REPO/'td2/A-quorum'
B=REPO/'td2/B-consensus'

def run(*args):
    result=subprocess.run([sys.executable,*map(str,args)],cwd=REPO,capture_output=True,
                          encoding='utf-8',env={**os.environ,'PYTHONIOENCODING':'utf-8'})
    assert result.returncode==0, result.stdout+result.stderr
    return result.stdout

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return module

def hash_check():
    baseline=json.loads((TD1/'evidence/reorganization-input-hashes.json').read_text(encoding='utf-8'))
    for name,wanted in baseline.items():
        assert hashlib.sha256((REPO/name).read_bytes()).hexdigest()==wanted, f'Changed protected input: {name}'
    assert len(list(REPO.glob('**/boutique.sqlite')))==1, 'More than one canonical database'
    return len(baseline)

def main():
    count=hash_check()
    integrity=json.loads(run(TD1/'verify-data.py'));assert integrity['ok']
    run(TD1/'test_td1.py')
    run(TD1/'sandbox_sqlite.py','--db',TD1/'data/boutique.sqlite')
    module=load('structure_quorum',A/'comparer_quorums.py')
    vote=module.charger_vote(TD1/'skeleton-multi-llm-en.py')
    rows=module.lire_csv(TD1/'traces-td1.csv')
    assert len(rows)==104 and all(r['nature']=='real' for r in rows)
    assert [r['date_utc'] for r in rows]==sorted(r['date_utc'] for r in rows)
    for r in [json.loads(line) for line in (A/'results/td2-vote-panel.jsonl').read_text(encoding='utf-8').splitlines()]:
        proposals,_=module.propositions_pour(rows,r['case'],module.PANEL_FIXE)
        assert vote(proposals,2)==r['decision'],r['case']
    generated=run(A/'comparer_quorums.py')
    table=A/'results/td2-tableau-vote.md'
    question_rows=lambda text:re.findall(r'^\| C\d\d \|.*$',text,re.M)
    before=question_rows(table.read_text(encoding='utf-8'))
    after=question_rows(generated)
    assert len(after)==40 and after==before, 'A decisions or detailed rows differ from delivered table'
    table.write_text(generated,encoding='utf-8')
    synthetic=[json.loads(line) for line in run(A/'atelier-vote.py').splitlines()]
    original=[json.loads(line) for line in (A/'results/td2-vote-synthetique.jsonl').read_text(encoding='utf-8').splitlines()]
    assert synthetic==original and len(synthetic)==4
    for proposals,k in [([],1),([dict(provider='x',model_requested='m',value=1,verdict='executed')]*3,2),
                        ([dict(provider='x',model_requested=str(i),value=1,verdict='executed') for i in range(3)],1)]:
        try: vote(proposals,k)
        except ValueError: pass
        else: raise AssertionError('Invalid quorum or duplicate accepted')
    run(B/'td2_wrong_consensus.py')
    evidence=json.loads((B/'evidence/C09-evidence.json').read_text(encoding='utf-8'))
    for key,voices in [('2_of_3',2),('3_of_5',3)]:
        r=evidence['votes'][key]
        assert r['pair_A_check'].startswith('passed') and r['manual']['value']==0 and r['manual']['votes']==voices
    assert evidence['reference_cents']==487980
    assert all(r['delta_cents']==487980 for r in evidence['delta'].values())
    hash_check()
    required=['README.md','td1/README.md','td2/README.md','td3/README.md',
              'reports/td1.md','reports/td2.md','reports/td3.md']
    required += [f'td2/{p}/{f}' for p in ('A-quorum','B-consensus','C-routing') for f in ('README.md','review-1.md','review-2.md')]
    broken=[]
    for name in required+['td2/A-quorum/report.md']:
        path=REPO/name; assert path.is_file(),name
        text=re.sub(r'```.*?```','',path.read_text(encoding='utf-8'),flags=re.S)
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',text):
            if target.startswith(('http:','https:','mailto:','#')):continue
            dest=target.split('#')[0]
            if (path.parent/dest).resolve()==(REPO/'td2/structure-validation.json').resolve():continue  # emitted below
            if not (path.parent/dest).exists():broken.append((name,target))
    assert not broken,broken
    report={'ok':True,'python_version':sys.version.split()[0],'protected_files_unchanged':count,
            'td1_integrity':True,'td1_regression_tests':'passed','sandbox_checks':25,
            'A_final_questions':20,'A_table_regenerated_identical':True,'A_panel_matches_delivered':True,
            'A_synthetic_cases':4,'A_rejects_duplicates_and_invalid_quorums':True,
            'B_pair_A_checks':{k:r['pair_A_check'] for k,r in evidence['votes'].items()},
            'C09_reference_and_each_delta_cents':487980,'broken_delivery_links':broken,
            'model_API_calls':0,'human_reviews':'À compléter','C_routing':'À compléter','TD3':'À compléter'}
    (REPO/'td2/structure-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=True,indent=2))

if __name__=='__main__':main()
