function openerp_pos_gift_voucher_models(instance, module){ //module is instance.point_of_sale
    var QWeb = instance.web.qweb,
    _t = instance.web._t;

    var PaymentlineSuper = module.Paymentline;
    module.Paymentline = module.Paymentline.extend({
        initialize: function(attributes, options){
            PaymentlineSuper.prototype.initialize.call(this, attributes, options);
            this.for_gift_voucher = options.cashregister.journal.for_gift_voucher;
            this.gift_voucher_serial = '';
            this.gift_voucher_validate = false;
            this.gift_voucher_spent = 0;
        },
        set_gift_voucher_serial: function(value){
            this.gift_voucher_serial = value;
        },
        get_gift_voucher_serial: function(){
            return this.gift_voucher_serial;
        },
        set_gift_voucher_validate: function(value){
            this.gift_voucher_validate = value;
        },
        get_gift_voucher_validate: function(){
            return this.gift_voucher_validate;
        },
        set_gift_voucher_spent: function(value){
            this.gift_voucher_spent = value;
        },
        get_gift_voucher_spent: function(){
            return this.gift_voucher_spent;
        },
        export_as_JSON: function(){
            var self = this;
            var res = PaymentlineSuper.prototype.export_as_JSON.call(this);
            res.for_gift_voucher = this.for_gift_voucher;
            res.gift_voucher_serial = this.get_gift_voucher_serial();
            res.gift_voucher_validate = this.get_gift_voucher_validate();
            res.gift_voucher_spent = this.get_gift_voucher_spent();
            return res;
        },
    });
}