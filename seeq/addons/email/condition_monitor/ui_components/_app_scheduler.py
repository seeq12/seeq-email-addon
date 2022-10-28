import traitlets
import ipyvuetify as v
from pathlib import Path
from ._condition import Condition
from ._tabs import Tabs
from seeq.addons.email.common.ui_components import Footer, Snackbar

CURRENT_DIR = Path(__file__).parent.resolve()
TEMPLATES_DIR = CURRENT_DIR.joinpath('vue_templates')
TEMPLATE_FILE = '_app_scheduler.vue'


class AppScheduler(v.VuetifyTemplate):
    """
    UI component - Layout of the Scheduler

    Attributes
    ----------
    template_file: str
        Modifies the VueTemplate.template_file attribute with the
        seeq.addons.email.condition_monitor.ui_components.vue_templates._app_scheduler.vue template
    """
    v.theme.themes.light.success = '#007960'
    v.theme.themes.light.primary = '#007960'
    v.theme.themes.light.info = '#2a5c84'

    template_file = str(TEMPLATES_DIR.joinpath(TEMPLATE_FILE))
    form_validated = traitlets.Bool(default_value=True, allow_none=True).tag(sync=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Components
        self.condition = Condition(**kwargs)
        self.tabs = Tabs(**kwargs)
        self.footer = Footer(**kwargs)
        self.snackbar = Snackbar(**kwargs)

        self.components = {
            'condition': self.condition,
            'tabs': self.tabs,
            'footie': self.footer,
            'snackbar': self.snackbar
        }
