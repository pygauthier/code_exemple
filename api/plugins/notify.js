import Vue from 'vue';

export default function({ app, $bvToast }, inject) {
    const toast = function(payload) {
        /*
            position (toaster):
                'b-toaster-top-right'
                'b-toaster-top-left'
                'b-toaster-top-center'
                'b-toaster-top-full'
                'b-toaster-bottom-right'
                'b-toaster-bottom-left'
                'b-toaster-bottom-center'
                'b-toaster-bottom-full'
        */
        const instance = new Vue(app);
        instance.$bvToast.toast(payload.text, {
            title: payload.message,
            autoHideDelay: payload.delay === undefined ? 5000 : payload.delay,
            appendToast: payload.append === undefined ? false : payload.append,
            variant: payload.type === undefined ? 'default' : payload.type,
            toaster: payload.position === undefined ? 'b-toaster-top-right' : payload.position,
        });
    };
    inject('notify', toast);
}
