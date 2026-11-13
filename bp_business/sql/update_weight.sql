UPDATE waybill 
SET total_weight = (
    SELECT COALESCE(SUM(wi.quantity * cg.avg_weight), 0)
    FROM waybill_item wi 
    JOIN cargo cg ON cg.cargo_id = wi.cargo_id 
    WHERE wi.waybill_id = %(waybill_id)s
) 
WHERE waybill_id = %(waybill_id)s;
