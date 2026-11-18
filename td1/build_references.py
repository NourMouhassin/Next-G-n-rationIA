"""Execute reference SQL and independently recompute from the original CSVs."""
import csv
import hashlib
import json
from datetime import date, datetime
from pathlib import Path
import sandbox_sqlite

ROOT = Path(__file__).resolve().parent
# Explicit transcription of the twenty questions: period, reference day, products.
# 'order' means completed age on each order's date.
SPECS = [
 ('2026-03-01','2026-06-01',None,None),
 (None,None,'2026-09-25',None),
 ('2026-01-01','2026-07-01',None,'abc'),
 ('2026-01-01','2026-10-01',None,None),
 ('2026-06-01','2026-06-02',None,None),
 ('2025-01-01','2026-01-01',None,None),
 ('2026-05-31','2026-06-01',None,None),
 (None,None,'2026-09-24',None),
 (None,None,'2026-09-26',None),
 (None,None,'order',None),
 (None,None,'2026-12-01',None),
 (None,None,None,'abc'),
 ('2026-04-01','2026-05-01',None,'ac'),
 ('2026-10-01','2026-12-01',None,'abc'),
 ('2026-03-01','2026-06-01','2026-09-25',None),
 (None,None,'2026-09-25','abc'),
 ('2026-01-01','2026-07-01','2026-09-25','abc'),
 ('2026-05-01','2026-06-01','order',None),
 ('2026-09-01','2026-10-01','2026-09-25','d'),
 ('2026-06-01','2026-09-01',None,None),
]

def read_csv(name):
    with (ROOT / name).open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))

def write_csv(name, fields, rows):
    with (ROOT / name).open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)

def reference_sql(spec):
    start, end, age, products = spec
    conditions = []
    if start:
        conditions += [f"o.date >= '{start} 00:00:00'", f"o.date < '{end} 00:00:00'"]
    if age:
        day = 'date(o.date)' if age == 'order' else f"'{age}'"
        conditions.append(f"(CAST(strftime('%Y', {day}) AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER) - (strftime('%m-%d', {day}) < strftime('%m-%d', c.birth_date))) = 25")
    if products:
        conditions.append('o.product_id IN (' + ','.join(repr(p) for p in products) + ')')
    return ('SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents '
            'FROM orders o JOIN product p ON p.product_id = o.product_id '
            'JOIN customers c ON c.customer_id = o.customer_id' +
            (' WHERE ' + ' AND '.join(conditions) if conditions else '') + ';')

def csv_totals():
    # Independently transcribed predicates, not generated from SPECS or SQL.
    prices = {r['product_id']: int(r['price']) for r in read_csv('data/product.csv')}
    births = {r['customer_id']: date.fromisoformat(r['birth_date']) for r in read_csv('data/customers.csv')}
    totals, counts = [0]*20, [0]*20
    for r in read_csv('data/orders.csv'):
        d = datetime.fromisoformat(r['date'])
        b = births[r['customer_id']]
        def period(s, e):
            return datetime.fromisoformat(s) <= d < datetime.fromisoformat(e)
        def age25(day):
            # Birthday-interval method, independent of SQLite year subtraction.
            return b.replace(year=b.year+25) <= day < b.replace(year=b.year+26)
        sep25 = age25(date(2026,9,25))
        abc = r['product_id'] in {'a','b','c'}
        matches = [
            period('2026-03-01','2026-06-01'), sep25,
            abc and period('2026-01-01','2026-07-01'),
            period('2026-01-01','2026-10-01'), period('2026-06-01','2026-06-02'),
            period('2025-01-01','2026-01-01'), period('2026-05-31','2026-06-01'),
            age25(date(2026,9,24)), age25(date(2026,9,26)), age25(d.date()),
            age25(date(2026,12,1)), abc,
            r['product_id'] in {'a','c'} and period('2026-04-01','2026-05-01'),
            abc and period('2026-10-01','2026-12-01'),
            sep25 and period('2026-03-01','2026-06-01'), sep25 and abc,
            sep25 and abc and period('2026-01-01','2026-07-01'),
            age25(d.date()) and period('2026-05-01','2026-06-01'),
            sep25 and r['product_id']=='d' and period('2026-09-01','2026-10-01'),
            period('2026-06-01','2026-09-01')]
        for i, match in enumerate(matches):
            if match:
                totals[i] += int(r['quantity_product']) * prices[r['product_id']]
                counts[i] += 1
    return totals, counts

def main():
    db = ROOT/'data/boutique.sqlite'
    before = hashlib.sha256(db.read_bytes()).hexdigest()
    totals, counts = csv_totals()
    rows, checks = [], []
    for i, spec in enumerate(SPECS):
        sql = reference_sql(spec)
        result = sandbox_sqlite.execute_query(db, sql)
        assert result['ok'] and result['shape_ok'] and result['columns']==['revenue_cents'], result
        assert type(result['value']) is int and result['value'] == totals[i], (i, result, totals[i])
        case = f'C{i+1:02}'
        rows.append(dict(case_id=case, sql=sql, revenue_cents=result['value']))
        checks.append(dict(case_id=case, sql_cents=result['value'], csv_cents=totals[i], matched_lines=counts[i], equal=True))
    assert before == hashlib.sha256(db.read_bytes()).hexdigest()
    write_csv('reference-td1.csv', ['case_id','sql','revenue_cents'], rows)
    write_csv('evidence/reference-check.csv', list(checks[0]), checks)
    print('20/20 SQL references equal independent CSV totals; database unchanged.')
    for r in checks:
        print(r['case_id'], r['sql_cents'], 'cents;', r['matched_lines'], 'lines')

if __name__ == '__main__':
    main()
