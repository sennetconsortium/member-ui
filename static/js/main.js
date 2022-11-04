
function Apps() {
    let classNames = {
        busy: 'is-busy'
    };

    let ToastIt;

    ToastIt = (function() {
        function ToastIt(el, options) {
            let defaults;
            defaults = {};
            this.ops = $.extend(defaults, options);
            this.el = $(el);
            this.events();
            return this;
        }

        ToastIt.prototype.handleToast = function(e) {
            const text = $(e.currentTarget).data('js-toastit')
            Toastify({
                text,
                ariaLive: 'polite'
            }).showToast()
        };

        ToastIt.prototype.events = function() {
            this.el.on('click', (function(e){
                if (!$(e.currentTarget).hasClass(classNames.busy))
                    this.handleToast(e)
            }).bind(this))
        };

        $.fn.ToastIt = function(options) {
            $(this).each(function(i, element) {
                return $(this).data('toastit', new ToastIt(this, options));
            });
        };
        return ToastIt;
    })();

    let ApiCall;
    ApiCall = (function() {
        function ApiCall(el, options) {
            this.isBusy = false
            this.el = $(el);
            this.events();
            return this;
        }

        ApiCall.prototype.showError = function() {
            Toastify({
                text: 'Something went wrong with your request.',
                style: {
                    background: '#f8d7da',
                    color: '#721c24',
                    'box-shadow': '0 3px 6px -1px rgb(0 0 0 / 12%), 0 10px 36px -4px rgb(232 77 151 / 30%)'
                }
            }).showToast()
        }

        ApiCall.prototype.unBusy = function ($el) {
            this.isBusy = false
            $el.removeClass(classNames.busy)
        }

        ApiCall.prototype.request = function(e) {
            e.preventDefault()
            let _t = this
            this.isBusy = true
            const $el = $(e.currentTarget)
            const url = $el.addClass(classNames.busy).data('js-apicall')
            $.ajax({
                type: "GET",
                url: "/downloads/members",
                xhrFields: {
                    responseType: 'blob'
                },
                success: function (data) {
                    if (!data.size) {
                        _t.showError()
                        _t.unBusy($el)
                        return
                    }
                    let a = document.createElement('a');
                    const url = window.URL.createObjectURL(data);
                    a.href = url;
                    a.download = $el.data('filename') || 'SenNet-file';
                    document.body.append(a);
                    a.click();
                    a.remove();
                    window.URL.revokeObjectURL(url)
                    _t.unBusy($el)
                },
                error: function (xhr, textStatus, errorThrown) {
                    console.error(textStatus)
                    _t.showError()
                    _t.unBusy($el)
                }
            });
        };

        ApiCall.prototype.events = function() {
            this.el.on('click', (function(e){
                if (!this.isBusy) {
                    this.request(e)
                }
            }).bind(this))
        };

        $.fn.ApiCall = function(options) {
            $(this).each(function(i, element) {
                return $(this).data('apicall', new ApiCall(this, options));
            });
        };
        return ApiCall;
    })();

    $('[data-js-toastit]').ToastIt()
    $('[data-js-apicall]').ApiCall()
}

(function() {
    $('document').ready(function() {
        Apps()
    });
}).call(this);
