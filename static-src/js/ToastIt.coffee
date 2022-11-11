###
    Used to create toast messages.
    Usage: $('[data-js-toastit]').ToastIt()
        <button data-js-toastit="Tell me something ...">Toast</button>
###
class ToastIt extends App
    constructor: (el, options) ->
        super(el, options)
        @events()

    handleToast: (e) ->
        text = @currentTarget(e).data(@tag)
        Toastify(
            text: text
            ariaLive: 'polite').showToast()
        return

    events: ->
        @el.on 'click', (e) =>
            if !@currentTarget(e).hasClass(@classes.busy)
                @handleToast e

_app(ToastIt)
