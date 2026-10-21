-- Запрос 4. Автомобили с грузоподъёмностью не меньше заданной
SELECT v.reg_number, v.brand, v.release_year, v.capacity,
       COUNT(w.waybill_id) AS trips
  FROM vehicle v
  LEFT JOIN waybill w ON w.vehicle_id = v.vehicle_id
 WHERE v.capacity >= %(min_capacity)s
 GROUP BY v.vehicle_id
 ORDER BY v.capacity DESC, v.reg_number;
