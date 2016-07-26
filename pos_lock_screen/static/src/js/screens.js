function openerp_pos_lock_screen_screens(instance,module){
    var QWeb = instance.web.qweb,
    _t = instance.web._t;

    module.LockScreenPopupWidget = module.PopUpWidget.extend({
        template: 'LockScreenPopupWidget',
        click_numpad_button: function($el,event){
            this.numpad_input($el.data('action'));
        },
        numpad_input: function(input) { //FIXME -> Deduplicate code
            var oldbuf = this.inputbuffer.slice(0);

            if (input === '.') {
                if (this.firstinput) {
                    this.inputbuffer = "0.";
                }else if (!this.inputbuffer.length || this.inputbuffer === '-') {
                    this.inputbuffer += "0.";
                } else if (this.inputbuffer.indexOf('.') < 0){
                    this.inputbuffer = this.inputbuffer + '.';
                }
            } else if (input === 'CLEAR') {
                this.inputbuffer = "";
            } else if (input === 'BACKSPACE') {
                this.inputbuffer = this.inputbuffer.substring(0,this.inputbuffer.length - 1);
            } else if (input === '+') {
                if ( this.inputbuffer[0] === '-' ) {
                    this.inputbuffer = this.inputbuffer.substring(1,this.inputbuffer.length);
                }
            } else if (input === '-') {
                if ( this.inputbuffer[0] === '-' ) {
                    this.inputbuffer = this.inputbuffer.substring(1,this.inputbuffer.length);
                } else {
                    this.inputbuffer = '-' + this.inputbuffer;
                }
            } else if (input[0] === '+' && !isNaN(parseFloat(input))) {
                this.inputbuffer = '' + ((parseFloat(this.inputbuffer) || 0) + parseFloat(input));
            } else if (!isNaN(parseInt(input))) {
                if (this.firstinput) {
                    this.inputbuffer = '' + input;
                } else {
                    this.inputbuffer += input;
                }
            }

            this.firstinput = this.inputbuffer.length === 0;

            if (this.inputbuffer !== oldbuf) {
                this.$('.value').text(this.inputbuffer);
            }
            pin_user = this.pos.db.get_user_bye_pin(this.inputbuffer);
            if (pin_user){
                for(var i = 0, len = this.pos.users.length; i < len; i++){
                    if (this.pos.users[i].id == pin_user.id){
                        //this.pos.user = this.pos.users[i]; //Cambia el cajero: Cuando se cree modulo que cambie el vendedor esto se quitara comentario
                        //POR OTRO MODULO HAREMOS QUE CAMBIE EL VENDEDOR
                        this.pos.get('selectedOrder').set_vendedor(pin_user);
                        this.pos.lock_screen = false;
                        this.pos.vendedor = pin_user;
                        //FIN
                        break;
                    }
                }
                self.pos_widget.screen_selector.close_popup();
            }
        },
        show: function(options){
            options = options || {};
            var self = this;
            this._super();

            this.message = options.message || '';
            this.comment = options.comment || '';
            this.inputbuffer = options.value   || '';
            this.renderElement();
            this.firstinput = true;

            this.$('.input-button,.mode-button').click(function(event){
                self.click_numpad_button($(this),event);
            });
            /*this.$('.button.cancel').click(function(){
                self.pos_widget.screen_selector.close_popup();
                if( options.cancel ){
                    options.cancel.call(self);
                }
            });

            this.$('.button.confirm').click(function(){
                self.pos_widget.screen_selector.close_popup();
                if( options.confirm ){
                    options.confirm.call(self,self.inputbuffer);
                }
            });*/
        },
    });
}