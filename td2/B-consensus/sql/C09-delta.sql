WITH reference_lines AS (
SELECT o.order_id, o.product_id, o.customer_id, o.date AS order_date, c.birth_date, o.quantity_product, p.price, o.quantity_product * p.price AS revenue_cents FROM  orders o JOIN product p ON p.product_id = o.product_id JOIN customers c ON c.customer_id = o.customer_id WHERE (CAST(strftime('%Y', '2026-09-26') AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER) - (strftime('%m-%d', '2026-09-26') < strftime('%m-%d', c.birth_date))) = 25
),
qwen_lines AS (
SELECT o.order_id, o.product_id, o.customer_id, o.date AS order_date, c.birth_date, o.quantity_product, p.price, o.quantity_product * p.price AS revenue_cents FROM  orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE (strftime('%Y', o.date) - strftime('%Y', c.birth_date)) = 25
  AND (strftime('%m-%d', o.date) >= strftime('%m-%d', c.birth_date))
  AND (strftime('%m-%d', o.date) < strftime('%m-%d', date(c.birth_date, '+26 years')))
),
cohere_lines AS (
SELECT o.order_id, o.product_id, o.customer_id, o.date AS order_date, c.birth_date, o.quantity_product, p.price, o.quantity_product * p.price AS revenue_cents FROM  customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE
  -- Compute age on 2026-09-26
  (
    -- Age = year difference
    CAST(SUBSTR(c.birth_date, 1, 4) AS INTEGER) -
    -- Subtract 1 if birthday hasn't occurred yet this year on 2026-09-26
    CASE
      WHEN SUBSTR(c.birth_date, 6, 2) > '09' THEN 1
      WHEN SUBSTR(c.birth_date, 6, 2) = '09' AND SUBSTR(c.birth_date, 9, 2) > '26' THEN 1
      ELSE 0
    END
  ) = 25
)
SELECT 'qwen' AS faulty_model, 'omitted' AS difference, a.* FROM reference_lines a WHERE NOT EXISTS (SELECT 1 FROM qwen_lines b WHERE b.order_id=a.order_id AND b.product_id=a.product_id)
UNION ALL
SELECT 'qwen' AS faulty_model, 'added' AS difference, a.* FROM qwen_lines a WHERE NOT EXISTS (SELECT 1 FROM reference_lines b WHERE b.order_id=a.order_id AND b.product_id=a.product_id)
UNION ALL
SELECT 'cohere' AS faulty_model, 'omitted' AS difference, a.* FROM reference_lines a WHERE NOT EXISTS (SELECT 1 FROM cohere_lines b WHERE b.order_id=a.order_id AND b.product_id=a.product_id)
UNION ALL
SELECT 'cohere' AS faulty_model, 'added' AS difference, a.* FROM cohere_lines a WHERE NOT EXISTS (SELECT 1 FROM reference_lines b WHERE b.order_id=a.order_id AND b.product_id=a.product_id)
ORDER BY faulty_model, difference, customer_id, order_id, product_id;
