-- Запрос 5. Сотрудники заданной должности
SELECT surname, address,
       TO_CHAR(birth_date, 'DD.MM.YYYY') AS birth_date,
       position,
       TO_CHAR(hire_date, 'DD.MM.YYYY') AS hire_date,
       DATE_PART('year', AGE(CURRENT_DATE, hire_date))::INT AS experience
  FROM staff
 WHERE position = %(position)s
 ORDER BY hire_date;
