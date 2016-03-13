--primero Ejecutar sql de pos_margin
select * from product_template;
--update pos_order_line set standard_price=0, gross_margin = 0
from pos_order, product_product
where pos_order.id = pos_order_line.order_id
	and pos_order_line.product_id = product_product.id
	and pack_parent_line_id is not null



--update pos_order_line set standard_price=(select sum(
from pos_order, product_product
where pos_order.id = pos_order_line.order_id
	and pos_order_line.product_id = product_product.id
	and pack_parent_line_id is not null
	and exists(select 1 from product_template 
			where product_template.id=product_product.tmpl_id
				and product_template.pack is True
		)