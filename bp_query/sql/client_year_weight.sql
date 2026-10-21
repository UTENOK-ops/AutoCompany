-- Запрос 6. Вес грузов клиентов с начала года (нарастающий итог) и скидка
SELECT contract_num, client_name, year_weight,
       CASE WHEN year_weight >= 30000 THEN 10
            WHEN year_weight >= 15000 THEN 5
            WHEN year_weight >= 5000  THEN 3
            ELSE 0 END AS discount
  FROM client
 ORDER BY year_weight DESC, client_name;
