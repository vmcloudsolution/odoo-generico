--actualiza costo de los q estan en cero
update pos_order_line set standard_price=COALESCE((	select ir_property.value_float
								from ir_property
								where 	ir_property.fields_id = (select ir_model_fields.id from ir_model_fields where ir_model_fields.name='standard_price' and ir_model_fields.model='product.template')
								    and ir_property.res_id like 'product.template,' || product_product.product_tmpl_id
							    ), 0)
from product_product
where   pos_order_line.product_id = product_product.id
	and coalesce(standard_price,0)=0



--update pos_order_line set standard_price=(select sum(
from pos_order, product_product
where pos_order.id = pos_order_line.order_id
	and pos_order_line.product_id = product_product.id
	and pack_parent_line_id is not null
	and exists(select 1 from product_template 
			where product_template.id=product_product.tmpl_id
				and product_template.pack is True
		)