#!/usr/bin/env python3
"""Generate reproducible TD2-C evidence from real repository files (offline).

Run from the cloned repository root:
    python td2/binome-C/produce_evidence.py

This never modifies TD1, A or B. It only writes evidence/td2-binome-C/.
"""
import csv
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OUT=ROOT/'evidence'/'td2-binome-C'


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    source=ROOT/'model-question-comparison-en.csv'
    if not source.exists():
        raise SystemExit('Missing repo root model-question-comparison-en.csv. Run in full group checkout.')
    route_path=HERE/'atelier-routage-adapte.py'
    results={}
    commands=[('scenarios-before.jsonl',[sys.executable,str(HERE/'atelier-routage-original.py')]),
              ('scenarios-after.jsonl',[sys.executable,str(route_path)]),
              ('scenarios-extra.jsonl',[sys.executable,str(route_path),'--extra']),
              ('family-rates.csv',[sys.executable,str(route_path),'--table']),
              ('routing-check.json',[sys.executable,str(route_path),'--check-rates'])]
    for name,command in commands:
        proc=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,check=True)
        (OUT/name).write_text(proc.stdout,encoding='utf-8')
        results[name]=len(proc.stdout.splitlines())
    # Unit tests use a self-contained status fixture matching the team's TD1
    # comparison; production runs above always use the actual repo table.
    tests=subprocess.run([sys.executable,str(HERE/'test_routage.py')],cwd=ROOT,
                         capture_output=True,text=True,check=True)
    (OUT/'tests.txt').write_text(tests.stdout+tests.stderr,encoding='utf-8')
    manifest={'type':'offline_reproduction_from_original_td1_comparison',
              'matrix_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
              'matrix_path':'model-question-comparison-en.csv',
              'catalog_path':'docs/paid-route-snapshot.json',
              'catalog_date':'2026-10-21',
              'question_count':20,'model_count':5,
              'test_suite':'15 deterministic unit tests; uses an independently constructed status-only fixture',
              'outputs':results,'network_calls':0,'api_keys_used':False,
              'external_availability_measured':False}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(manifest,indent=2,ensure_ascii=False))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
