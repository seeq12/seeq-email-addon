import traitlets
import ipyvuetify as v
from typing import Callable
from pathlib import Path

CURRENT_DIR = Path(__file__).parent.resolve()
TEMPLATES_DIR = CURRENT_DIR.joinpath('vue_templates')
TEMPLATE_FILE = '_footer.vue'


class Footer(v.VuetifyTemplate):
    """
    UI component - Footer

    Attributes
    ----------
    stopped_job_warning: str, default None
        Warning for stopping a job
    unschedule_button_disabled: bool, default True
        Bool that sets whether the button is disabled (True) or enable (False)
    schedule_button_disabled: bool, default True
        Bool that sets whether the button is disabled (True) or enable (False)
    template_file: str
        Modifies the VueTemplate.template_file attribute with the
        seeq.addons.email.condition_monitor.ui_components.vue_templates._footer.vue template
    """

    template_file = str(TEMPLATES_DIR.joinpath(TEMPLATE_FILE))
    stopped_job_warning = traitlets.Unicode(default_value='').tag(sync=True)
    unschedule_button_disabled = traitlets.Bool(default_value=True).tag(sync=True)
    unschedule_button_loading = traitlets.Bool(default_value=False).tag(sync=True)
    schedule_button_disabled = traitlets.Bool(default_value=True).tag(sync=True)
    schedule_button_loading = traitlets.Bool(default_value=False).tag(sync=True)

    def __init__(self,
                 *args,
                 unschedule_button_on_click: Callable[[dict], None] = None,
                 schedule_button_on_click: Callable[[dict], None] = None,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.unschedule_button_on_click = unschedule_button_on_click
        self.schedule_button_on_click = schedule_button_on_click

    def vue_unschedule_button_on_click(self, data):
        if not self.unschedule_button_on_click:
            return
        if self.unschedule_button_on_click is not None:
            self.unschedule_button_on_click(data)

    def vue_schedule_button_on_click(self, data):
        if not self.schedule_button_on_click:
            return
        if self.schedule_button_on_click is not None:
            self.schedule_button_on_click(data)
