from anthrax.frontend import Frontend

def dummy_view(*args, **kwargs):
    return ''

dummy_frontend = Frontend({
    'text_input': dummy_view,
    'long_text_input': dummy_view,
}, dummy_view)
