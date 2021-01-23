odoo.define('web_one2many_selectable.ListRenderer', function (require) {
	"use strict";

	var core = require('web.core');
	var ListRenderer = require('web.ListRenderer');
	var field_registry = require('web.field_registry');
	var FieldOne2Many = require('web.relational_fields').FieldOne2Many;

ListRenderer.include({
    events: _.extend({}, ListRenderer.prototype.events, {
        "click .cf_button_confirm": "_action_selected_lines",
    }),
    init: function (parent, state, params) {
        var self = this;
        this._super.apply(this, arguments);
        if (this.arch.attrs.selected_row && this.arch.attrs.selected_row == "true"){
            this.hasSelectors = true;
        }
    },
});

var One2ManySelectable = FieldOne2Many.extend({
		template: 'One2ManySelectable',
		events: {
			"click .cf_button_confirm": "action_selected_lines",
		},
		_getRenderer: function () {
            var self = this;
            var res = this._super.apply(this, arguments);
            var list_buttons = JSON.parse(this.attrs.list_buttons);
            //Se poner en duro la creacion de botones porque no se encontro la forma de asignar el parametro de la function action_selected_lines
            //Problema: se sobrescribe el evento click con el ultimo boton creado
            for (var i = 0; i < list_buttons.length; i++) {
                if (i==0){
                    var $button1 = $("<button  icon='gtk-yes' class='"+list_buttons[i].name+" oe_button' href='javascript:void(0)'>"+list_buttons[i].string+"</button>");
                    $button1.on('click', function() {
                        self.action_selected_lines('confirm_selectable_line_1')
                    });
                    $button1.appendTo(this.$(".js_selectable_button_array"));
                }
                if (i==1){
                    var $button2 = $("<button  icon='gtk-yes' class='"+list_buttons[i].name+" oe_button' href='javascript:void(0)'>"+list_buttons[i].string+"</button>");
                    $button2.on('click', function() {
                        self.action_selected_lines('confirm_selectable_line_2')
                    });
                    $button2.appendTo(this.$(".js_selectable_button_array"));
                }
                if (i==2){
                    var $button3 = $("<button  icon='gtk-yes' class='"+list_buttons[i].name+" oe_button' href='javascript:void(0)'>"+list_buttons[i].string+"</button>");
                    $button3.on('click', function() {
                        self.action_selected_lines('confirm_selectable_line_3')
                    });
                    $button3.appendTo(this.$(".js_selectable_button_array"));
                }
            }
            return res
        },
		get_text: function(){
		    return this.attrs.string_button || 'Confirmar'
		},
		action_selected_lines: function(method)
		{
			//event.stopPropagation();
			//event.preventDefault();
			var self=this;
			var selected_ids = self.get_selected_ids_one2many();
			if (selected_ids.length === 0)
			{
				this.do_warn("Seleccione un registro");
				return false;
			}
			this._rpc({
                model: this.model,
                method: method,//evugor
                args: [this.res_id, selected_ids],
            }).then(function (result) {
                //self.trigger_up('reload');
                self.do_action({
                    name: 'Comprobante',
                    res_model: result.res_model,
                    res_id: result.res_id,
                    views: [[false, 'form']],
                    type: 'ir.actions.act_window',
                });
            });
		},
		//collecting the selected IDS from one2manay list
		get_selected_ids_one2many: function ()
		{
			var self = this;
			var ids =[];
			this.$el.find('td.o_list_record_selector input:checked')
					.closest('tr').each(function () {
					    var str_id = $(this).data('id');
					    for (var i = 0; i < self.record.data.fees_detail_ids.data.length; i++) {//Hardcode => fees_detail_ids
                            if(self.record.data.fees_detail_ids.data[i].id === str_id){
                                ids.push(self.record.data.fees_detail_ids.data[i].res_id);
                            }
                        }
			});
			return ids;
		},


	});
	field_registry.add('one2many_selectable', One2ManySelectable);

	return {
        One2ManySelectable: One2ManySelectable
    };

});
