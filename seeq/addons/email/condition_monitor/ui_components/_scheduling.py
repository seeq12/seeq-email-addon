import traitlets
import ipyvuetify as v
from pathlib import Path

CURRENT_DIR = Path(__file__).parent.resolve()
TEMPLATES_DIR = CURRENT_DIR.joinpath('vue_templates')
TEMPLATE_FILE = '_scheduling.vue'


class Scheduling(v.VuetifyTemplate):
    """
    UI component - Scheduling tab

    Attributes
    ----------
    to: str, default None
        String value of the To field.
    schedule: str, default None
        String value of the Schedule field.
    topic_url: str, default None
        String value of the Topic URL field.
    time_zone_value: str, default None
        String value of selected time zone.
    time_zone_items: list, default list()
        List of available time zones.
    lookback_period: str, default None
        String value of the look_back_value field.
    cc: str, default None
        String value of the Cc field.
    bcc: str, default None
        String value of the Bcc field.
    scheduling_form_valid: bool, default True
        If True, the form that wraps the To and Schedule fields is marked
        as valid. Otherwise, the form is invalid.
    template_file: str
        Modifies the VueTemplate.template_file attribute with the
        seeq.addons.email.condition_monitor.ui_components.vue_templates._scheduling.vue template
    """

    template_file = str(TEMPLATES_DIR.joinpath(TEMPLATE_FILE))
    to = traitlets.Unicode(default_value=None, allow_none=True).tag(sync=True)
    schedule = traitlets.Unicode(default_value=None, allow_none=True).tag(sync=True)
    topic_url = traitlets.Unicode(default_value=None, allow_none=True).tag(sync=True)
    time_zone_value = traitlets.Unicode(default_value=None, allow_none=True).tag(sync=True)
    time_zone_items = traitlets.List(default_value=[]).tag(sync=True)
    lookback_period = traitlets.Unicode(default_value=None, allow_none=True).tag(sync=True)
    cc = traitlets.Unicode(default_value=None, allow_none=True).tag(sync=True)
    bcc = traitlets.Unicode(default_value=None, allow_none=True).tag(sync=True)
    scheduling_form_valid = traitlets.Bool(default_value=True, allow_none=True).tag(sync=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.time_zone_items = self.time_zone_items if kwargs.get('time_zone_items') is None \
            else kwargs.get('time_zone_items')
