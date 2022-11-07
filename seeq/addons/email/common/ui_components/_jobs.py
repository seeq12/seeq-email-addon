import traitlets
import ipyvuetify as v
from pathlib import Path

CURRENT_DIR = Path(__file__).parent.resolve()
TEMPLATES_DIR = CURRENT_DIR.joinpath('vue_templates')
TEMPLATE_FILE = '_jobs.vue'


class Jobs(v.VuetifyTemplate):
    """
    UI component - Jobs tab

    Attributes
    ----------
    data_table_headers: list, default list()
        List of table headers.
    data_table_items: dict, default list()
        Dictionary with the table records.
    data_table_items: list, default list()
        List to control selected rows.
    template_file: str
        Modifies the VueTemplate.template_file attribute with the
        seeq.addons.email.condition_monitor.ui_components.vue_templates._jobs.vue template
    """

    template_file = str(TEMPLATES_DIR.joinpath(TEMPLATE_FILE))
    data_table_headers = traitlets.List(default_value=[]).tag(sync=True)
    data_table_items = traitlets.List(default_value=[], allow_none=True).tag(sync=True)
    data_table_values = traitlets.List(default_value=[], allow_none=True).tag(sync=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_table_headers = list() if kwargs.get('data_table_headers') is None else kwargs.get(
            'data_table_headers')
        self.data_table_items = list() if kwargs.get('data_table_items') is None else kwargs.get('data_table_items')
