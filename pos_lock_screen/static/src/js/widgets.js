function openerp_pos_lock_screen_widgets(instance,module){
    var QWeb = instance.web.qweb,
    _t = instance.web._t;
    var module = instance.point_of_sale;

    module.LockScreenButton = instance.web.Widget.extend({
        template: 'LockScreenButton',
        init: function(parent, options){
            this._super(parent, options);
            this.pos = options.pos || (parent ? parent.pos : undefined);
        },
        renderElement: function() {
            var self = this;
            this._super();
            this.$el.click(function(){
                self.pos.lock_screen = true;
                self.pos.LockScreen()
            });
        }
    });

    module.posPosWidget = module.PosWidget.include({
        template: 'PosWidget',

        init: function(parent, options) {
            this._super(parent);
            var  self = this;
        },
        build_widgets: function() {
            var self = this;
            this._super();
            this.LockScreen = new module.LockScreenPopupWidget(this, {});
             this.LockScreen.appendTo(this.$el);
            this.screen_selector.add_popup('lock_screen',this.LockScreen);

            this.LockScreenButton = new module.LockScreenButton(this, {});
            this.LockScreenButton.replace(this.$('.LockScreenButton'));
        },
    });
}