function openerp_pos_lock_screen_models(instance, module){
    var PosModelSuper = module.PosModel

    var _initialize_ = module.PosModel.prototype.initialize;
    var PosModelSuper = module.PosModel;
    module.PosModel = module.PosModel.extend({
        initialize: function(session, attributes) {
            this.lock_screen = true; //Variable que indica si se bloquea la pantalla
            this.user_last_PIN = false; //Variable que indica cual fue el ultimo PIN valido usado
            this.vendedor = {};
            PosModelSuper.prototype.initialize.call(this, session,attributes);
        },
        LockScreen: function(message='Ingrese su código PIN', change_vendedor=true){
            var self = this;
            if (this.lock_screen){
                self.pos_widget.screen_selector.show_popup('lock_screen',{
                    'message':(message),
                    'change_vendedor': change_vendedor,
                });
            }
        },
        push_order: function(order) {
            result = PosModelSuper.prototype.push_order.call(this, order);
            if (this.config.lockscreen_every_order == true){
                this.lock_screen = true;
            }
            return result;
        },
        add_new_order: function(){
            var self = this;
            result = PosModelSuper.prototype.add_new_order.call(this);
            this.get('selectedOrder').set_vendedor(this.vendedor);
            setTimeout(function(){
               self.LockScreen();
            },800);
            return result;
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