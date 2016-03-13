select * from pos_order_line 
where gross_margin =0
limit 100;
--update pos_order_line set standard_price=0, gross_margin=0;

--update pos_order_line set standard_price = (	select value_float
						from ir_property
						where 	ir_property.fields_id = (select ir_model_fields.id from ir_model_fields where ir_model_fields.name='standard_price' and ir_model_fields.model='product.template')
						    and ir_property.res_id like 'product.template,' || product_product.product_tmpl_id
					    )
from pos_order, product_product
where pos_order.id = pos_order_line.order_id
	and pos_order_line.product_id = product_product.id;

--update pos_order_line set gross_margin = price_subtotal_incl - (standard_price * qty)
from pos_order, product_product
where pos_order.id = pos_order_line.order_id
	and pos_order_line.product_id = product_product.id;
	

