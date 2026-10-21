-- Запрос 1. Клиенты в пределах / за пределами МКАД
SELECT contract_num, client_name, address,
       CASE WHEN inside_mkad THEN 'В пределах МКАД' ELSE 'За пределами МКАД' END AS zone,
       contact_surname, contact_phone
  FROM client
 WHERE %(zone)s = 'all'
    OR inside_mkad = (%(zone)s = 'inside')
 ORDER BY contract_num;
