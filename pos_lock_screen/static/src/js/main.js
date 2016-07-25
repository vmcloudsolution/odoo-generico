openerp.pos_lock_screen = function(instance){

    var module = instance.point_of_sale;

    openerp_pos_lock_screen_screens(instance,module);
    openerp_pos_lock_screen_widgets(instance,module);
    openerp_pos_lock_screen_models(instance,module);
    openerp_pos_lock_screen_db(instance,module);
};
