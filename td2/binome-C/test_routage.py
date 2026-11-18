#!/usr/bin/env python3
"""Offline tests. Prefer actual repo TD1 table if installed; otherwise a labelled
100-cell status-only snapshot transcribed from the group's 18 Nov GitHub files.
The fixture is for reproducible unit tests, NOT a new model measurement.
"""
import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('route_c',HERE/'atelier-routage-adapte.py')
route=importlib.util.module_from_spec(spec)
spec.loader.exec_module(route)

MODEL_KEYS=[
    'groq:openai/gpt-oss-120b',
    'groq:openai/gpt-oss-20b',
    'openrouter:cohere/north-mini-code:free',
    'groq:qwen/qwen3.8-27b',
    'openrouter:dots-studio/dots-3-note-preview:free',
]
# Case statuses from the team's actual 100-cell final comparison (no numerical
# answer or API call generated here). U=unrun; X=invalid SQL; I=incorrect.
FAULTS={
    MODEL_KEYS[0]: {'C15':'incorrect'},
    MODEL_KEYS[1]: {'C02':'incorrect','C11':'incorrect'},
    MODEL_KEYS[2]: {f'C{i:02d}':'incorrect' for i in [2,8,9,10,11,15,17,18,19]},
    MODEL_KEYS[3]: {**{f'C{i:02d}':'incorrect' for i in [9,15,17,19]},'C16':'not_executed'},
    MODEL_KEYS[4]: {**{f'C{i:02d}':'incorrect' for i in [2,8,9,10,11,18]},'C17':'sql_invalid'},
}
EXPECTED_RATES={
    'F1_period':[6,6,6,6,6],
    'F2_age_date':[4,2,0,3,0],
    'F2b_age_order':[1,1,0,1,0],
    'F3_product':[4,4,4,4,4],
    'F4_combined':[4,5,1,1,3],
}


def generate_fixture(root):
    root=Path(root)
    (root/'docs').mkdir(parents=True,exist_ok=True)
    config={'modeles':[{'gate':k.split(':',1)[0],'identifiant_exact':k.split(':',1)[1]}
                       for k in MODEL_KEYS]}
    (root/'modeles-autorises.json').write_text(json.dumps(config))
    catalog={'retrieved_date':'2026-10-21','models':[
      {'id':'openai/gpt-oss-120b','pricing':{'prompt':'0.00000015','completion':'0.00000060'}},
      {'id':'openai/gpt-oss-20b','pricing':{'prompt':'0.000000018','completion':'0.000000090'}},
      {'id':'qwen/qwen3.8-27b','pricing':{'prompt':'0.00000004','completion':'0.00000135'}},
      {'id':'cohere/north-mini-code:free','pricing':{'prompt':'0','completion':'0'}},
      {'id':'dots-studio/dots-3-note-preview:free','pricing':{'prompt':'0','completion':'0'}}]}
    (root/'docs'/'paid-route-snapshot.json').write_text(json.dumps(catalog))
    with (root/'model-question-comparison-en.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=['case_id','model_id','status'])
        writer.writeheader()
        for i in range(1,21):
            case=f'C{i:02d}'
            for key in MODEL_KEYS:
                writer.writerow({'case_id':case,'model_id':key,'status':FAULTS[key].get(case,'correct')})


class RoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        cls.root=Path(cls.temp.name)
        generate_fixture(cls.root)
        cls.policy,cls.models,cls.catalog,cls.rates=route.load_inputs(cls.root)
        cls.resources=route.make_resources(cls.policy,cls.models,cls.catalog,cls.rates)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_family_counts(self):
        for fam,expected in EXPECTED_RATES.items():
            self.assertEqual([self.rates[(fam,k)]['correct'] for k in MODEL_KEYS],expected)

    def test_strict_eligibility(self):
        only=[r for r in self.resources if r['access']=='free' and 'F4_combined' in r['families']]
        self.assertEqual([r['model'] for r in only],[MODEL_KEYS[1]])
        only=[r for r in self.resources if r['access']=='free' and 'F2_age_date' in r['families']]
        self.assertEqual([r['model'] for r in only],[MODEL_KEYS[0]])

    def test_published_price(self):
        paid={r['model']:r['cash'] for r in self.resources if r['access']=='tokens'}
        self.assertAlmostEqual(paid[MODEL_KEYS[1]],0.0000387,12)
        self.assertAlmostEqual(paid[MODEL_KEYS[0]],0.0002775,12)
        self.assertNotIn(MODEL_KEYS[2],paid)
        self.assertNotIn(MODEL_KEYS[4],paid)

    def test_seven_official_scenario_intents(self):
        scenarios=route.scenarios(self.resources)
        self.assertEqual([s[0] for s in scenarios],
          ['simple','complex','deferrable','urgent','budget exhausted','high impact','unknown capability'])
        got={name:route.choose(req,resources,self.policy,self.rates) for name,req,resources in scenarios}
        self.assertEqual({k:v['action'] for k,v in got.items()},
                         {'simple':'run','complex':'run','deferrable':'defer','urgent':'run',
                          'budget exhausted':'abstain','high impact':'run','unknown capability':'abstain'})
        self.assertEqual(got['simple']['resource'],MODEL_KEYS[2])
        self.assertEqual(got['complex']['resource'],MODEL_KEYS[1])
        self.assertEqual(got['deferrable']['wake_in_minutes'],60)
        self.assertEqual(got['urgent']['resource'],'paid:'+MODEL_KEYS[1])
        self.assertIn('human',got['high impact']['checks'])
        self.assertIsNone(got['unknown capability']['resource'])

    def test_provider_down_fallback(self):
        name,req,resources=route.extra_scenarios(self.resources)[0]
        self.assertEqual(route.choose(req,resources,self.policy,self.rates)['resource'],MODEL_KEYS[4])

    def test_age_date_route(self):
        name,req,resources=route.extra_scenarios(self.resources)[1]
        decision=route.choose(req,resources,self.policy,self.rates)
        self.assertEqual(decision['resource'],MODEL_KEYS[0])
        self.assertIn('reference SQL',decision['checks'])

    def test_age_order_payout_requires_human_review(self):
        name,req,resources=route.extra_scenarios(self.resources)[3]
        d=route.choose(req,resources,self.policy,self.rates)
        self.assertEqual(d['resource'],MODEL_KEYS[1])
        self.assertIn('human',d['checks'])

    def test_age_date_free_exhaustion_defers(self):
        name,req,resources=route.extra_scenarios(self.resources)[2]
        d=route.choose(req,resources,self.policy,self.rates)
        self.assertEqual((d['action'],d['wake_in_minutes']),('defer',20))

    def test_no_free_and_no_money_abstains(self):
        name,req,resources=route.scenarios(self.resources)[4]
        d=route.choose(req,resources,self.policy,self.rates)
        self.assertEqual(d['action'],'abstain')

    def test_unseen_family_abstains(self):
        d=route.choose({'family':'new_unknown','use':'dashboard'},self.resources,self.policy,self.rates)
        self.assertEqual(d['action'],'abstain')

    def test_included_subscription_before_wait(self):
        # Controlled, explicitly synthetic illustration of the official kit's
        # priority rule. No subscription route of these models is claimed.
        request={'family':'F4_combined','use':'dashboard','budget':0.30,
                 'deadline_minutes':120,'can_wait':True}
        exhausted=[dict(r,available=False,reset_minutes=5) if r['access']=='free' else dict(r)
                   for r in self.resources]
        subscription={'id':'ILLUSTRATIVE_INCLUDED_SUBSCRIPTION','model':MODEL_KEYS[1],
                      'access':'subscription','cash':0,'allocation':0.04,
                      'available':True,'reset_minutes':None,'families':['F4_combined']}
        d=route.choose(request,exhausted+[subscription],self.policy,self.rates)
        self.assertEqual((d['action'],d['resource']),('run','ILLUSTRATIVE_INCLUDED_SUBSCRIPTION'))

    def test_undocumented_route_is_not_free(self):
        self.assertIsNone(route.paid_cost(self.catalog,'cohere/north-mini-code:free',{'input':650,'output':300}))

    def test_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);generate_fixture(root)
            with (root/'model-question-comparison-en.csv').open('a',encoding='utf-8') as f:
                f.write(f'C01,{MODEL_KEYS[0]},correct\n')
            with self.assertRaises(ValueError):route.load_inputs(root)

    def test_missing_cell_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);generate_fixture(root)
            p=root/'model-question-comparison-en.csv'
            lines=p.read_text().splitlines();p.write_text('\n'.join(lines[:-1])+'\n')
            with self.assertRaises(ValueError):route.load_inputs(root)

    def test_check_descriptions_are_proposed_not_performed(self):
        d=route.choose({'family':'F2_age_date','use':'customer','budget':0.3,
                        'can_wait':False,'deadline_minutes':1},self.resources,self.policy,self.rates)
        self.assertIn('reference SQL',d['checks'])
        self.assertNotIn('verified',d)


if __name__=='__main__':
    unittest.main(verbosity=2)
