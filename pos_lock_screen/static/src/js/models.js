function openerp_pos_lock_screen_models(instance, module){
    var PosModelSuper = module.PosModel

    var _initialize_ = module.PosModel.prototype.initialize;
    var PosModelSuper = module.PosModel;
    module.PosModel = module.PosModel.extend({
        initialize: function(session, attributes) {
            this.lock_screen = true;
            PosModelSuper.prototype.initialize.call(this, session,attributes);
        },
        push_order: function(order) {
            PosModelSuper.prototype.push_order.call(this, order);
            if (this.lock_screen){
                self.pos_widget.screen_selector.show_popup('lock_screen',{
                    'message':('Ingrese su código PIN'),
                });
            }
        },
    });
    module.PosModel.prototype.models.push({
        model: 'res.users',
        fields: ['name', 'pin_code'],
        domain: [['pin_code','!=',false]],
        loaded: function(self,list_users){
            self.list_users = list_users;
            self.db.add_list_users(list_users);
        },
    });
}