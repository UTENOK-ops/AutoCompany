-- Заголовок накладной для запроса 3
SELECT w.waybill_id,
       TO_CHAR(w.waybill_date, 'DD.MM.YYYY') AS waybill_date,
       c.client_name,
       v.brand || ' (' || v.reg_number || ')' AS vehicle,
       s.surname AS forwarder,
       w.total_weight
  FROM waybill w
  JOIN client  c ON c.contract_num = w.contract_num
  JOIN vehicle v ON v.vehicle_id   = w.vehicle_id
  JOIN staff   s ON s.staff_id     = w.forwarder_id
 WHERE w.waybill_id = %(waybill_id)s;
