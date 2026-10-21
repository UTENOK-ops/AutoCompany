-- Запрос 3. Состав товарно-транспортной накладной
SELECT cg.cargo_name,
       wi.quantity,
       cg.avg_weight,
       wi.quantity * cg.avg_weight AS item_weight
  FROM waybill_item wi
  JOIN cargo cg ON cg.cargo_id = wi.cargo_id
 WHERE wi.waybill_id = %(waybill_id)s
 ORDER BY item_weight DESC;
