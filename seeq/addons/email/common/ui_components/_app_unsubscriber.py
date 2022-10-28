import traitlets
from typing import Callable
import ipyvuetify as v
from pathlib import Path
from ._snackbar import Snackbar

CURRENT_DIR = Path(__file__).parent.resolve()
TEMPLATES_DIR = CURRENT_DIR.joinpath('vue_templates')
TEMPLATE_FILE = '_app_unsubscriber.vue'


class AppUnsubscriber(v.VuetifyTemplate):
    """
    UI component - Layout of the Unsubscriber

    Attributes
    ----------
    template_file: str
        Modifies the VueTemplate.template_file attribute with the
        seeq.addons.email.condition_monitor.ui_components.vue_templates._app_unsubscriber.vue template
    """
    v.theme.themes.light.success = '#007960'
    v.theme.themes.light.primary = '#007960'
    v.theme.themes.light.info = '#2a5c84'

    template_file = str(TEMPLATES_DIR.joinpath(TEMPLATE_FILE))
    form_validated = traitlets.Bool(default_value=True, allow_none=True).tag(sync=True)
    email_addresses = traitlets.Unicode(default_value='').tag(sync=True)
    unsubscribe_button_loading = traitlets.Bool(default_value=False).tag(sync=True)
    valid_emails = traitlets.Bool(default_value=False).tag(sync=True)

    def __init__(self,
                 *args,
                 unsubscribe_click: Callable[[dict], None] = None,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.email_addresses = self.email_addresses if kwargs.get('email_addresses') is None else kwargs.get(
            'email_addresses')

        self.unsubscribe_click = unsubscribe_click

        # Components
        self.snackbar = Snackbar(**kwargs)
        self.components = {
            'snackbar': self.snackbar
        }

    def vue_unsubscribe_click(self, data):
        if not self.unsubscribe_click:
            return
        if self.unsubscribe_click is not None:
            self.unsubscribe_click(data)
