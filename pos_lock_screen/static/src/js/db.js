function openerp_pos_lock_screen_db(instance,module){
    module.PosDB = module.PosDB.extend({
        init: function(options){
            this._super(parent,options);
            this.list_users = [];
            this.users_bye_pin = {};
        },
        add_list_users: function(list_users){
            for(var i = 0, len = list_users.length; i < len; i++){
                var user = list_users[i];
                this.list_users.push(user);
                this.users_bye_pin[user.pin_code] = user;
            }
        },
        get_user_bye_pin: function(pin){
            return this.users_bye_pin[pin];
        },
    });
}