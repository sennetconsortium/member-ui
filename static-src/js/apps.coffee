(->
  $('document').ready ->
    $('[data-js-toastit]').ToastIt()
    $('[data-js-apicall]').ApiCall()
    return
  return
).call this