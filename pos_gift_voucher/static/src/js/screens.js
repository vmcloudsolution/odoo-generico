function openerp_pos_gift_voucher_screens(instance,module){
    var QWeb = instance.web.qweb,
    _t = instance.web._t;
    module.PaymentScreenWidget = module.PaymentScreenWidget.extend({
        init: function(parent, options) {
            this._super(parent,options);
            var self = this;

            this.gift_voucher_change_handler = function(event){
                var node = this;
                while(node && !node.classList.contains('paymentline')){
                    node = node.parentNode;
                }
                if(node){
                    node.line.set_gift_voucher_serial(this.value);
                    node.line.gift_voucher_validate = false;
                }
                self.set_amount_gift_voucher(0)
                self.set_gift_voucher_validate(false)
                self.set_gift_voucher_spent(0);
            };

            this.line_gift_voucher_button_handler = function(event){
                var count = 0;
                gift_voucher_serial = self.get_gift_voucher_serial();
                self.pos.get('selectedOrder').get('paymentLines').each(function(paymentline){
                    if (paymentline.for_gift_voucher == true && paymentline.gift_voucher_serial == gift_voucher_serial){
                        count += 1;
                    }
                });
                if (count > 1){
                    self.pos_widget.screen_selector.show_popup('error',{
                        'message':_t('Duplicate gift voucher'),
                        'comment':_t('Duplicate gift voucher'),
                    });
                    return
                }
                partner = self.pos.get('selectedOrder').get_client()
                self.call_gift_voucher_amount(partner ? partner.id : false, gift_voucher_serial);
            };
        },
        validate_amount: function(result){
            var self = this;
            if (result[1] == false) {
                if (result[2] != '') {
                    mensaje = result[2]
                }else{
                    mensaje = 'The gift voucher is invalid or has already redeemed'
                }
                self.pos_widget.screen_selector.show_popup('error',{
                    'message':_t('Invalid voucher'),
                    'comment':_t(mensaje),
                });
                return false;
            }
//            if (result[1] > 0) {
//                self.pos_widget.screen_selector.show_popup('error',{
//                    'message':_t('Vale correcto!!'),
//                    'comment':_t(''),
//                });
//            }
            /*if (amount > self.pos.get('selectedOrder').getTotalTaxIncluded()){
                self.pos_widget.screen_selector.show_popup('error',{
                    'message':_t('Verify the amount'),
                    'comment':_t('Gift voucher amount must be less or equal to the order'),
                });
                return false;
            }*/
            return true;
        },
        call_gift_voucher_amount: function(partner, gift_voucher_serial){
            var self = this;
            new instance.web.Model('pos.gift.voucher').call('get_voucher_amount',[partner, gift_voucher_serial]).then(function(result){
                if (!self.validate_amount(result)){
                    return false;
                }
                self.pos_widget.screen_selector.show_popup('error',{
                    'message':_t('Vale correcto!!'),
                    'comment':_t(''),
                });
                self.set_amount_gift_voucher(result[0])
                self.set_gift_voucher_validate(true)
                self.set_gift_voucher_spent(result[1])
            },function(err,event){
                event.preventDefault();
                self.pos_widget.screen_selector.show_popup('error-traceback',{
                    'message':_t('It is not a valid gift voucher'),
                    'comment':_t('Failed to get Gift voucher'),
                });
            });
        },
        get_gift_voucher_serial: function(){
            var selected_line =this.pos.get('selectedOrder').selected_paymentline;
            if(selected_line){
                return selected_line.get_gift_voucher_serial();
            }
            return false
        },
        set_amount_gift_voucher: function(val) {
            var selected_line =this.pos.get('selectedOrder').selected_paymentline;
            if(selected_line){
                selected_line.set_amount(val);
                selected_line.node.querySelector('input').value = selected_line.amount.toFixed(2);
            }
            this.update_payment_summary()
        },
        set_gift_voucher_validate: function(val) {
            var selected_line =this.pos.get('selectedOrder').selected_paymentline;
            if(selected_line){
                selected_line.set_gift_voucher_validate(val);
            }
        },
        set_gift_voucher_spent:function(val) {
            var selected_line =this.pos.get('selectedOrder').selected_paymentline;
            if(selected_line){
                selected_line.set_gift_voucher_spent(val);
            }
        },
        render_paymentline: function(line){
            var self = this;
            var el_node = this._super(line);
            el_node.querySelector('.paymentline-input-gift-voucher')
                .addEventListener('keyup', this.gift_voucher_change_handler);
            el_node.querySelector('.pos-gift-voucher-button')
                .addEventListener('click', this.line_gift_voucher_button_handler);
            return el_node;
        },
    });
}