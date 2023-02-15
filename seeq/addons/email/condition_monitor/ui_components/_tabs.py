import ipyvuetify as v
from pathlib import Path
from seeq.addons.email.common.ui_components import Templating, Jobs
from ._scheduling import Scheduling

CURRENT_DIR = Path(__file__).parent.resolve()
TEMPLATES_DIR = CURRENT_DIR.joinpath('vue_templates')
TEMPLATE_FILE = '_tabs.vue'


class Tabs(v.VuetifyTemplate):
    """
    UI component - Tabs section

    Attributes
    ----------
    template_file: str
        Modifies the VueTemplate.template_file attribute with the
        seeq.addons.email.condition_monitor.ui_components.vue_templates._tabs.vue template
    """

    template_file = str(TEMPLATES_DIR.joinpath(TEMPLATE_FILE))

    # buttonDisabled = traitlets.Bool(default_value=True).tag(sync=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Components
        self.scheduling_tab_content = Scheduling(**kwargs)
        self.templates_tab_content = Templating(**kwargs)
        self.jobs_tab_content = Jobs(**kwargs)

        self.components = {
            'scheduling-content': self.scheduling_tab_content,
            'templating-content': self.templates_tab_content,
            'jobs-content': self.jobs_tab_content
        }
