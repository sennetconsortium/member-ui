class ApiCall extends App
    constructor: (el, options) ->
        super(el, options)
        @isBusy = false
        @options = options
        @el = $(el)
        @events()

    showError: ->
        Toastify(
            text: 'Something went wrong with your request.'
            style:
                background: '#f8d7da'
                color: '#721c24'
                'box-shadow': '0 3px 6px -1px rgb(0 0 0 / 12%), 0 10px 36px -4px rgb(232 77 151 / 30%)').showToast()

    unBusy: ($el) ->
        @isBusy = false
        $el.removeClass @classes.busy

    handleBlob: (e, data) =>
        $el = @currentTarget(e)
        if !data.size
            @showError()
            @unBusy $el
        else
            a = document.createElement('a')
            url = window.URL.createObjectURL(data)
            a.href = url
            a.download = $el.data('filename') or 'SenNet-file'
            document.body.append a
            a.click()
            a.remove()
            window.URL.revokeObjectURL url
            @unBusy $el

    request: (e) ->
        e.preventDefault()
        @isBusy = true
        $el = @currentTarget(e)
        url = $el.addClass(@classes.busy).data('js-apicall')
        action = $el.data('action')
        $.ajax
            type: 'GET' || $el.data('method')
            url: url or @options.url
            xhrFields:
                responseType: action or @options.action
            success: (data) =>
                if (action == 'blob')
                    @handleBlob(e, data)
            error: (xhr, textStatus, errorThrown) =>
                console.error textStatus
                @showError()
                @unBusy $el

    events: ->
        @el.on 'click', (e) =>
            if !@isBusy
                @request e

_app(ApiCall)

