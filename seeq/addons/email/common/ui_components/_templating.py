import traitlets
import ipyvuetify as v
import ipywidgets as widgets
from typing import Callable
from pathlib import Path

CURRENT_DIR = Path(__file__).parent.resolve()
TEMPLATES_DIR = CURRENT_DIR.joinpath('vue_templates')
TEMPLATE_FILE = '_templating.vue'


class Templating(v.VuetifyTemplate):
    """
    UI component - Templates tab

    Attributes
    ----------
    templating_explanation: ipywidgets, default None
        Instructions text to be rendered as HTML.
    subject: str, default None
        String value of the email subject.
    html: str, default None
        String value of the email HTML template.
    templating_form_valid: bool, default True
        If True, the form that wraps the Subject Template and HTML Template fields is marked
        as valid. Otherwise, the form is invalid.
    template_file: str
        Modifies the VueTemplate.template_file attribute with the
        seeq.addons.email.condition_monitor.ui_components.vue_templates._templating.vue template
    """

    template_file = str(TEMPLATES_DIR.joinpath(TEMPLATE_FILE))
    templating_explanation = traitlets.Any().tag(sync=True, **widgets.widget_serialization)
    subject = traitlets.Unicode(default_value=None, allow_none=True).tag(sync=True)
    html = traitlets.Unicode(default_value=None, allow_none=True).tag(sync=True)
    reset_button_disabled = traitlets.Bool(default_value=True).tag(sync=True)
    templating_form_valid = traitlets.Bool(default_value=True, allow_none=True).tag(sync=True)

    def __init__(self,
                 *args,
                 template_reset_on_click: Callable[[dict], None] = None,
                 **kwargs):
        super().__init__(*args, **kwargs)
        explanation_text = '' if kwargs.get('templating_explanation') is None else kwargs.get('templating_explanation')
        self.templating_explanation = widgets.HTML(explanation_text)

        self.template_reset_on_click = template_reset_on_click

    def vue_template_reset_on_click(self, data):
        if not self.template_reset_on_click:
            return
        if self.template_reset_on_click is not None:
            self.template_reset_on_click(data)
