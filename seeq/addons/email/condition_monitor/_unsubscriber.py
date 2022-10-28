from seeq import spy
import re
import warnings
from seeq.addons.email.common.ui_components import AppUnsubscriber
from seeq.addons.email.common import get_ids_from_query_parameters
from ._installer import NOTIFIER_NOTEBOOK_NAME

warnings.filterwarnings('ignore')


class Unsubscriber:

    def __init__(self, jupyter_notebook_url, notifier_notebook_url=None):
        ids_from_query_params = get_ids_from_query_parameters(jupyter_notebook_url)
        workbook_id = ids_from_query_params.get('workbook_id')
        condition_id = ids_from_query_params.get('condition_id')

        if not workbook_id or not condition_id:
            raise ValueError(
                'Workbook and Condition IDs must be supplied as query parameters in the URL for this Notebook')

        self.workbook_id = workbook_id
        self.condition_id = condition_id

        p = re.compile(r'\/(notebooks|apps)\/(.*)\/.+$')
        self.notifier_notebook_url = p.sub(rf'/\1/\2/{NOTIFIER_NOTEBOOK_NAME}', jupyter_notebook_url) \
            if notifier_notebook_url is None else notifier_notebook_url

        self.app = AppUnsubscriber(unsubscribe_click=self.on_unsubscribe,
                                   email_addresses=spy.user.email)

    # The character limit on job indices is too small to use guids - use a shortened guid instead.
    def short_id(self, guid):
        return guid[-12:]

    def on_error(self, e):
        message = str(e.message) if hasattr(e, 'message') else str(e)

        self.app.snackbar.color = 'red darken-2'
        self.app.snackbar.message = 'Something went wrong: ' + message
        self.app.snackbar.timeout = '5000'
        self.app.snackbar.value = True

    def on_success(self, message):
        self.app.snackbar.color = 'success'
        self.app.snackbar.message = message
        self.app.snackbar.timeout = '5000'
        self.app.snackbar.value = True

    def on_close_snackbar(self, *_):
        self.app.snackbar.value = False

    def on_unsubscribe(self, *_):
        self.app.unsubscribe_button_loading = True
        try:
            jobs_df = spy.jobs.pull(datalab_notebook_url=self.notifier_notebook_url, label=self.workbook_id, all=True)
            if jobs_df is None or jobs_df.empty or self.short_id(self.condition_id) not in jobs_df.index:
                self.app.unsubscribe_button_loading = False
                self.on_error(RuntimeError(f'This notification is no longer scheduled for Workbook ID'
                                           f'{self.workbook_id} and Condition ID {self.condition_id}'))
                return
            referenced_job = jobs_df.loc[self.short_id(self.condition_id)]
            all_address_fields_empty = True
            for address_type in ['To', 'Cc', 'Bcc']:
                if not address_type in referenced_job:
                    continue
                addresses_of_type = referenced_job[address_type].split(',')
                addresses_to_remove = [address.strip() for address in self.app.email_addresses.split(',')]
                updated_addresses = [updated_address.strip() for updated_address in addresses_of_type
                                     if updated_address.strip() not in addresses_to_remove]
                address_update = ','.join(updated_addresses)
                if address_update:
                    all_address_fields_empty = False
                jobs_df.loc[self.short_id(self.condition_id), address_type] = address_update

            if all_address_fields_empty:
                jobs_df.drop(index=self.short_id(self.condition_id), inplace=True)
            spy.jobs.push(
                jobs_df,
                datalab_notebook_url=self.notifier_notebook_url,
                label=self.workbook_id,
                quiet=True
            )
            self.app.unsubscribe_button_loading = False
            unscheduled_affix = '.  No recipients remain, so the notification job was unscheduled.' \
                if all_address_fields_empty else ''
            self.on_success(f'Unsubscribed{unscheduled_affix}')
        except Exception as e:
            self.app.unsubscribe_button_loading = False
            self.on_error(e)
            return

    def run(self):
        return self.app
