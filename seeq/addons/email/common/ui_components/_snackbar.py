import traitlets
import ipyvuetify as v
from pathlib import Path

CURRENT_DIR = Path(__file__).parent.resolve()
TEMPLATES_DIR = CURRENT_DIR.joinpath('vue_templates')
TEMPLATE_FILE = '_snackbar.vue'


class Snackbar(v.VuetifyTemplate):
    """
    UI component - Snackbar

    Attributes
    ----------
    snackbar_value: bool, default False
        Whether the snackbar is displayed (True).
    snackbar_message: str, default ''
        Message to show in the snackbar.
    snackbar_color: str, default 'success'
        Color of the snackbar.
    template_file: str
        Modifies the VueTemplate.template_file attribute with the
        seeq.addons.email.condition_monitor.ui_components.vue_templates._snackbar.vue template
    """

    template_file = str(TEMPLATES_DIR.joinpath(TEMPLATE_FILE))
    value = traitlets.Bool(default_value=False).tag(sync=True)
    message = traitlets.Unicode(default_value='').tag(sync=True)
    color = traitlets.Unicode(default_value='success').tag(sync=True)
    timeout = traitlets.Unicode(default_value='4000').tag(sync=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
