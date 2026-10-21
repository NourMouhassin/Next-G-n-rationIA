"""Offline regression tests. Mock answers never enter the experimental files."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import td1

s = td1.s

class OfflineTests(unittest.TestCase):
    def test_reference_recomputation(self):
        values, _ = td1.ref.csv_totals()
        for i, row in enumerate(td1.ref.read_csv('reference-td1.csv')):
            self.assertEqual(s.judge(td1.ROOT/'data/boutique.sqlite', row['sql'], values[i])['verdict'], 'correct')
            self.assertEqual(int(row['revenue_cents']), values[i])

    def test_retry_policy(self):
        for status, wait, expected in [(429,3,3),(429,61,None),(429,None,None),(403,None,None),(501,None,5),(200,None,None)]:
            r = s.ReponseLLM('mock', http_status=status, retry_after_s=wait, error='HTTP error')
            self.assertEqual(s.retry_delay(r),expected)
        self.assertIsNone(s.retry_delay(s.ReponseLLM('mock', error='network: DNS failure')))
        self.assertEqual(s.retry_delay(s.ReponseLLM('mock', error='timeout after 45s')),5)

    def test_raw_and_missing_measurements(self):
        r = s.ReponseLLM('mock')
        raw = b'{"model":"mock","choices":[{"message":{"content":"SELECT"},"finish_reason":"length"}]}'
        s.parse_completion(raw,r)
        self.assertEqual(r.raw_response,raw.decode())
        self.assertEqual(r.finish_reason,'length')
        self.assertIsNone(r.tokens_prompt)
        self.assertIsNone(r.cost_native)

    def test_free_parameters(self):
        clients = s.clients_from_config(td1.CONFIG)
        self.assertEqual(len(clients),5)
        for c,m in zip(clients,td1.CONFIG['modeles']):
            body=c.body('system','user')
            self.assertEqual(body['temperature'],0)
            self.assertEqual(c.timeout,45)
            for k,v in m['parametres'].items():
                self.assertEqual(body[k],v)
            if c.provider=='openrouter':
                self.assertTrue(c.model_id.endswith(':free'))
                self.assertEqual(body['provider']['max_price'],{'prompt':0,'completion':0})

    def test_retry_saved_and_resume_skips(self):
        class Fake(s.ClientLLM):
            paced=False
            def __init__(self):
                super().__init__('mock','mock')
                self.calls=0
            def _appeler(self,*args):
                self.calls+=1
                if self.calls==1:
                    return s.ReponseLLM('mock',http_status=503,error='HTTP 503',nature='simulation')
                return s.ReponseLLM('mock',http_status=200,text='SELECT 0 AS revenue_cents',nature='simulation')
        # Exercise HTTP-like retry and persist both original answers to a temporary state.
        with tempfile.TemporaryDirectory() as tmp, patch.object(s.time,'sleep'):
            path=Path(tmp)/'test.jsonl'
            table=s.TableTraces(path)
            client=Fake()
            case=next(q for q in td1.QUESTIONS if q['id']=='C06')
            orch=s.Orchestrateur([client],td1.ROOT/'data/boutique.sqlite',td1.SCHEMA,{'C06':0},table)
            def save(answer):
                table.ajouter(orch.tracer('mock:mock:C06',client,case,s.build_prompt(td1.SCHEMA,case['question'])[2],answer,0))
            client.interroger('system','user','C06',on_answer=save)
            loaded=s.TableTraces(path)
            self.assertEqual([r.attempts for r in loaded.lignes],[1,2])
            self.assertTrue(loaded.verified('mock:mock:C06','simulation'))
            self.assertEqual(loaded.lignes[-1].verdict,'correct')

    def test_no_retry_on_resume_without_permission(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(s.time,'sleep'):
            c=s.ClientHTTP('groq','mock',td1.CONFIG['groq'])
            case=td1.QUESTIONS[0]
            table=s.TableTraces(Path(tmp)/'state.jsonl')
            orch=s.Orchestrateur([c],td1.ROOT/'data/boutique.sqlite',td1.SCHEMA,{'C01':792800},table)
            answer=s.ReponseLLM('mock',http_status=429,error='HTTP 429',retry_after_s=90)
            table.ajouter(orch.tracer('groq:mock:C01',c,case,s.build_prompt(td1.SCHEMA,case['question'])[2],answer,792800))
            with patch.object(c,'_appeler',side_effect=AssertionError('must not call')):
                orch.interroger_tous(case)

    def test_shape_and_alias_enforced(self):
        for sql in ('SELECT 0 AS wrong_name','SELECT 0 AS revenue_cents, 1','SELECT 0 AS revenue_cents UNION ALL SELECT 0'):
            self.assertEqual(s.judge(td1.ROOT/'data/boutique.sqlite',sql,0)['verdict'],'sql_invalid')

    def test_final_matrix(self):
        rows=td1.ref.read_csv('model-question-comparison-en.csv')
        self.assertEqual(len(rows),100)
        self.assertEqual(len({r['cell_id'] for r in rows}),100)
        for r in rows:
            if not r['trace_file']:
                self.assertEqual(r['status'],'not_executed')
                self.assertEqual(r['value_cents'],'')

if __name__=='__main__':
    unittest.main(verbosity=2)
