odoo.define('pos_ticket.models', function (require) {
"use strict";

var PosBaseWidget = require('point_of_sale.BaseWidget');
var chrome = require('point_of_sale.chrome');
var gui = require('point_of_sale.gui');
var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var core = require('web.core');
var Model = require('web.DataModel');

var QWeb = core.qweb;
var _t = core._t;

var posmodel_super = models.PosModel.prototype;
models.PosModel = models.PosModel.extend({
    initialize: function(session, attributes) {
        this.pos_etiquetera = null;
        posmodel_super.initialize.call(this,session, attributes);
    },
    push_and_invoice_order: function(order){
        //Se quita funcionalidad de creacion de factura
        var self = this;
        var pushed = new $.Deferred();
        pushed = this.push_order(order, {to_invoice:true});
        return pushed;
    },
});

models.PosModel.prototype.models.push({
    model: 'pos.etiquetera',
    fields: [],
    loaded: function(self,pos_etiquetera){
        self.pos_etiquetera = pos_etiquetera[0]
        console.log("EVUGOR:77777", self.pos_etiquetera)
    },
});

var _super_order = models.Order.prototype;
models.Order = models.Order.extend({
    export_as_JSON: function() {
        var json = _super_order.export_as_JSON.apply(this,arguments);
        json.to_invoice   = this.to_invoice
        return json;
    },
});

});
