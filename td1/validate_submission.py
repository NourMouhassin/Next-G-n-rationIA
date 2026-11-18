"""Run the documented offline checks; save real outputs and a concise report."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parent

def main():
    checks=[]
    commands=[
        ['td1.py','prepare'],
        ['test_td1.py'],
        ['sandbox_sqlite.py','--db','data/boutique.sqlite','--out','evidence/sandbox-tests.json'],
        ['verify-data.py'],
    ]
    for i, args in enumerate(commands,1):
        result=subprocess.run([sys.executable,*args],cwd=ROOT,text=True,capture_output=True)
        output=result.stdout+result.stderr
        (ROOT/f'evidence/check-{i}.txt').write_text(output,encoding='utf-8')
        checks.append({'command':'python '+' '.join(args),'exit_code':result.returncode,'output':f'evidence/check-{i}.txt'})
    # Never print matching secrets. This scans the intended source tree, not parent key files.
    suspect=[]
    forbidden=[]
    patterns=[rb'gsk_[A-Za-z0-9]{20,}',rb'sk-or-v1-[A-Za-z0-9]{20,}',rb'gh[pousr]_[A-Za-z0-9]{25,}',rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----']
    for path in ROOT.rglob('*'):
        if not path.is_file() or any(p in ('.git','__pycache__','.venv') for p in path.relative_to(ROOT).parts):
            continue
        if path.name.startswith(('.env','private_api_keys')):
            forbidden.append(str(path.relative_to(ROOT)))
        if any(re.search(pattern,path.read_bytes()) for pattern in patterns):
            suspect.append(str(path.relative_to(ROOT)))
    ok=all(c['exit_code']==0 for c in checks) and not suspect and not forbidden
    records=[json.loads(line) for line in (ROOT/'traces-td1.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
    report={'ok':ok,'python_version':sys.version.split()[0],'checks':checks,'possible_secret_files':suspect,'forbidden_files':forbidden,'database_sha256':hashlib.sha256((ROOT/'data/boutique.sqlite').read_bytes()).hexdigest(),'human_peer_review':'pending','real_model_calls':sum(r['nature']=='real' for r in records)}
    (ROOT/'evidence/validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
    return 0 if ok else 1

if __name__=='__main__':
    raise SystemExit(main())
