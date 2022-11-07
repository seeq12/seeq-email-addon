import traitlets
import ipyvuetify as v
from typing import Callable
from pathlib import Path

CURRENT_DIR = Path(__file__).parent.resolve()
TEMPLATES_DIR = CURRENT_DIR.joinpath('vue_templates')
TEMPLATE_FILE = '_condition.vue'


class Condition(v.VuetifyTemplate):
    """
    UI component - Condition section

    Attributes
    ----------
    condition_value: str, default None
        String value of the current condition selected.
    condition_items: list
        List of conditions.
    template_file: str
        Modifies the VueTemplate.template_file attribute with the
        seeq.addons.email.condition_monitor.ui_components.vue_templates._condition.vue template
    """

    template_file = str(TEMPLATES_DIR.joinpath(TEMPLATE_FILE))
    condition_value = traitlets.Unicode(default_value=None, allow_none=True).tag(sync=True)
    condition_items = traitlets.List(default_value=[]).tag(sync=True)

    def __init__(self,
                 *args,
                 condition_select_on_change: Callable[[str], None] = None,
                 **kwargs
                 ):
        super().__init__(*args, **kwargs)
        self.condition_items = self.condition_items if kwargs.get('condition_items') is None else kwargs.get(
            'condition_items')
        self.condition_select_on_change = condition_select_on_change

    def vue_condition_select_on_change(self, data):
        if not self.condition_select_on_change:
            return
        if self.condition_select_on_change is not None:
            self.condition_select_on_change(data)
