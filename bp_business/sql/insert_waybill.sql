INSERT INTO waybill (waybill_date, contract_num, vehicle_id, forwarder_id, total_weight)
VALUES (%(date)s, %(contract_num)s, %(vehicle_id)s, %(forwarder_id)s, 0) 
RETURNING waybill_id;