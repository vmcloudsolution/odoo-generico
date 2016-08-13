function openerp_pos_print_gift_voucher(instance, module){
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    module.Voucher  = Backbone.Model.extend({
        initialize: function(attributes){
            return this;
        },
        print_receipts: function(receipts){
            var self = this;
            this.proxy_url = "http://localhost:8069"
            this.proxy = new module.ProxyDeviceBackend(this);
            this.proxy.connect(this.proxy_url)
            _.each(receipts,function(receipt){
                self.proxy.print_receipt(QWeb.render('XmlPrintVoucher',{
                    receipt: receipt, widget: self,
                }));
            });
        },
        print_voucher: function(voucher_ids) {
            var self = this;
            new instance.web.Model('pos.gift.voucher').call('export_for_printing',[voucher_ids]).then(function(voucher_receipt){
                self.print_receipts(voucher_receipt);
                return true;
            },function(err,event){
                event.preventDefault();
                console.log("Error")
            });
            return true
        },
    });

    instance.web.client_actions.add('print_voucher_action', 'instance.pos_gift_voucher_print.action');
    instance.pos_gift_voucher_print.action = function (instance, context) {
        this.voucher_ids = []
        this.Voucher = new module.Voucher(this);
        if (context.context.voucher_ids) this.voucher_ids = context.context.voucher_ids;
        this.Voucher.print_voucher(this.voucher_ids);
    };
};