class App
    constructor: (el, options) ->
        @ops = options
        @el = $(el)
        @tag = 'js-' + options.appName.toLowerCase()
        @classes =
            busy: 'is-busy'

    currentTarget: (e) ->
        return $(e.currentTarget)


_app = (fn) ->
    $.fn[fn.name] = (ops = {}) ->
        $(this).each (i, element) ->
            ops.appName = fn.name
            $(this).data fn.name, new fn(this, ops)