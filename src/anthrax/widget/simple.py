from anthrax.widget.base import Widget

class TextInput(Widget):
    """Simple text input"""
    supress_too_long = True
    supress_bad_regexp = False

class LongTextInput(TextInput):
    """Multirow text input"""
    columns = 80
    rows = 25

