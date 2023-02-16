import re
from IPython.display import clear_output
from bs4 import BeautifulSoup
import pandas as pd
import ipywidgets as w
import ipyvuetify as v
import pytz
import requests
import warnings
from seeq import spy
from seeq.addons.email.condition_monitor.ui_components import AppScheduler
from seeq.addons.email.common import get_ids_from_query_parameters, get_seeq_url
from ._installer import NOTIFIER_NOTEBOOK_NAME, UNSUBSCRIBER_NOTEBOOK_NAME

warnings.filterwarnings('ignore')


class ConditionMonitorScheduler:
    TEMPLATING_EXPLANATION = """
    <p style="line-height:1.5; margin-bottom:10px; font-size:14px">
      Enter your template HTML below. Note that not all HTML tags or CSS attributes
      will be rendered by email clients. You can validate your template by sending
      yourself test emails or using an online checker like 
      <a href="https://www.htmlemailcheck.com/check/" target="_blank">https://www.htmlemailcheck.com/check/</a>.
      Some advanced editors, e.g., VSCode, will also validate HTML.
    </p>
    <p style="line-height:1.5; margin-bottom:10px; font-size:14px">
      Within your template, you can also access variables specific to this notifier job.
      The fields Condition Name, Condition ID, Schedule, Lookback Interval, Topic Document URL,
      and Workbook ID are supported within the <code>job</code> context. You can insert these special
      variables into your email by referencing the <code>job</code> context, followed by the name of
      the name of the variable enclosed by double-quotes and square brackets.
    </p>
    <p style="line-height:1.5; margin-bottom:10px; font-size:14px">For example:</p>
    <p style="line-height:1.5; margin-bottom:10px; font-size:14px">
      <strong>Condition Name:</strong> {job["Condition Name"]}
      <br>
      <strong>Topic Document URL:</strong> {job["Topic Document URL"]}
    </p>
    <p style="line-height:1.5; margin-bottom:10px; font-size:14px">
      You can access information about the triggering capsule in a similar manner -
      for example, capsule start or end and custom capsule properties.
    </p>
    <p style="line-height:1.5; margin-bottom:10px; font-size:14px">
      <strong>Capsule Start:</strong> {capsule["Capsule Start"]}
      <br>
      <strong>Capsule Property (ex. "Batch ID"):</strong> {capsule["Batch ID"]}
    </p>
    <p style="line-height:1.5; margin-bottom:10px; font-size:14px">
      Any elements that have a class of "seeq-auto-update" may be modified by this Notebook upon scheduling.
      For example, the Topic Document URL field is optional, so if one is not provided, the paragraph element
      with class <code>"seeq-auto-update"</code> and id <code>"tdu"</code> will be removed from the default
      template.
    </p>
    """
    SUBJECT_TEMPLATE_DEFAULT = 'Capsule alert for Condition {job["Condition Name"]}'
    HTML_TEMPLATE_DEFAULT = """
        <html>
            <head></head>
            <body>
                <b>Capsule alert!</b>
                <p>A new capsule was identified in the Scheduled Email Sender with Capsule Start {capsule["Capsule 
                Start"]}</p>
                <p>Capsule details:</p>
                <p><b>Start Time: </b>{capsule["Capsule Start"]}</p>
                <p><b>End Time: </b>{capsule["Capsule End"]}</p>
                <p class="seeq-auto-update" id="tdu">Topic Document: <a href='{job["Topic Document URL"]}'>link</a></p>
                <a class="seeq-auto-update" id="usu" href='unsubscriber_notebook_url'>Unsubscribe</a>
            </body>
        </html>
    """

    TO_DEFAULT = ''
    SCHEDULE_DEFAULT = 'Every 6 hours'
    LOOKBACK_DEFAULT = '1.5'
    TIME_ZONE_DEFAULT = 'UTC'
    CC_DEFAULT = ''
    BCC_DEFAULT = ''
    TOPIC_DEFAULT = ''
    DEFAULT_JOB_PARAMETERS = {
        'Condition ID': '',
        'Condition Name': '',
        'Schedule': SCHEDULE_DEFAULT,
        'Time Zone': TIME_ZONE_DEFAULT,
        'Lookback Interval': LOOKBACK_DEFAULT,
        'To': TO_DEFAULT,
        'Cc': CC_DEFAULT,
        'Bcc': BCC_DEFAULT,
        'Topic Document URL': TOPIC_DEFAULT,
        'Subject Template': SUBJECT_TEMPLATE_DEFAULT,
        'Html Template': HTML_TEMPLATE_DEFAULT,
        'Workbook ID': '',
        'Scheduled': False,
        'Stopped': False,
        'Inception': ''
    }

    def __init__(self, jupyter_notebook_url, notifier_notebook_url=None, unsubscriber_notebook_url=None):
        ids_from_query_params = get_ids_from_query_parameters(jupyter_notebook_url)
        workbook_id = ids_from_query_params.get('workbook_id')
        worksheet_id = ids_from_query_params.get('worksheet_id')

        if not workbook_id or not worksheet_id:
            raise Exception(
                'Workbook and Worksheet IDs must be supplied as query parameters in the URL for this Notebook')

        self.selected_condition = None
        p = re.compile(r'\/(notebooks|apps)\/(.*)\/.+$')
        self.notifier_notebook_url = p.sub(rf'/\1/\2/{NOTIFIER_NOTEBOOK_NAME}', jupyter_notebook_url) \
            if notifier_notebook_url is None else notifier_notebook_url
        self.unsubscriber_notebook_url = p.sub(rf'/\1/\2/{UNSUBSCRIBER_NOTEBOOK_NAME}', jupyter_notebook_url) \
            if unsubscriber_notebook_url is None else unsubscriber_notebook_url
        self.HTML_TEMPLATE_DEFAULT.replace('unsubscriber_notebook_url', self.unsubscriber_notebook_url)
        self.jobs = pd.DataFrame()
        self.workbook_id = workbook_id
        self.worksheet_id = worksheet_id
        self.DEFAULT_JOB_PARAMETERS['To'] = spy.user.email

        self.output = w.Output()

        self.app = AppScheduler(templating_explanation=self.TEMPLATING_EXPLANATION,
                                time_zone_items=pytz.all_timezones,
                                template_reset_on_click=self.on_reset_templates,
                                condition_select_on_change=self.on_condition_select,
                                schedule_button_on_click=self.on_schedule,
                                unschedule_button_on_click=self.on_unschedule,
                                )
        self.check_email_configured()
        self.initialize_jobs()

        self.selected_condition = None
        self.set_conditions()

        if self.jobs.empty or self.selected_condition not in self.jobs.index:
            unschedule_button_disabled = True
        else:
            unschedule_button_disabled = pd.Series([self.jobs.loc[self.selected_condition, 'Scheduled']]).bool()

        self.app.footer.schedule_button_disabled = self.selected_condition is None or self.app.form_validated is False
        self.app.footer.unschedule_button_disabled = unschedule_button_disabled

        if self.selected_condition:
            self.set_models_from_selected_job()
        self.app.template.reset_button_disabled = self.selected_condition is None
        self.set_data_table()

    # The character limit on job indices is too small to use guids - use a shortened guid instead.
    @staticmethod
    def short_id(guid):
        return guid[-12:]

    def get_source_worksheet_url(self):
        host = spy.client.host[:-4]
        return f'{host}/workbook/{self.workbook_id}/worksheet/{self.worksheet_id}'

    def check_email_configured(self):
        p = re.compile(r'/(notebooks|apps)/(.*)$')
        notifier_notebook_contents_url = p.sub(r'/api/contents/\2', self.notifier_notebook_url)
        notifier_notebook = requests.get(notifier_notebook_contents_url, cookies={'sq-auth': spy.client.auth_token})
        default_email_text = """'Email Address': 'email.sender@mycompany.com'"""
        if not notifier_notebook.text.find(default_email_text) == -1:
            edit_notifier_url = self.notifier_notebook_url.replace('/apps/', '/notebooks/')
            error_html = v.Html(tag='p',
                                children=[
                                    'Configure SMTP settings in ',
                                    v.Html(tag='a', attributes={'href': edit_notifier_url, 'target': '_blank'},
                                           children=['Notifier Notebook'], style_='color: #B1D7CF'),
                                    ' before using Scheduler'
                                ])
            self.on_error(error_html)

    def get_existing_jobs(self):
        try:
            pulled_jobs = spy.jobs.pull(datalab_notebook_url=self.notifier_notebook_url,
                                        label=self.workbook_id, all=True)
        except (spy.errors.SPyValueError, spy.errors.SPyRuntimeError, spy.errors.SPyException):
            pulled_jobs = None
        existing_jobs = pd.DataFrame(columns=list(self.DEFAULT_JOB_PARAMETERS.keys())) \
            if pulled_jobs is None or pulled_jobs.empty \
            else pulled_jobs
        if not existing_jobs.empty:
            existing_jobs['Scheduled'] = True
        return existing_jobs.astype({'Stopped': 'bool'})

    def get_conditions_from_worksheet(self):
        with self.output:
            worksheet_items = spy.search(self.get_source_worksheet_url(), quiet=True)
            clear_output()
        if worksheet_items.empty:
            conditions_from_worksheet = pd.DataFrame()
        else:
            conditions_from_worksheet = worksheet_items[worksheet_items['Type'].str.contains('Condition')]
            conditions_from_worksheet.index = [
                self.short_id(guid) for guid in conditions_from_worksheet['ID'].to_list()
            ]
        return conditions_from_worksheet

    def initialize_jobs(self):
        self.jobs = self.get_existing_jobs()
        for key, condition in self.get_conditions_from_worksheet().iterrows():
            if key in self.jobs.index:
                # Rename from worksheet in case the name in the pickled job DataFrame is stale
                self.jobs.loc[key, 'Condition Name'] = condition['Name']
            else:
                new_job = pd.Series(self.DEFAULT_JOB_PARAMETERS)
                new_job.name = self.short_id(condition['ID'])
                new_job['Condition ID'] = condition['ID']
                new_job['Condition Name'] = condition['Name']
                new_job['Stopped'] = False
                new_job['Scheduled'] = False
                self.jobs = self.jobs.append(new_job)

    def displayable_conditions(self):
        unscheduled = [
            {'text': job['Condition Name'], 'value': index} for index, job
            in self.jobs[self.jobs['Scheduled'] == False].iterrows()
        ]
        previously_scheduled = [
            {'text': job['Condition Name'], 'value': index} for index, job
            in self.jobs[self.jobs['Scheduled'] == True].iterrows()]

        formatted_conditions = []
        if unscheduled:
            formatted_conditions += [{'header': 'From Worksheet or Unscheduled'}] + unscheduled
        if previously_scheduled:
            formatted_conditions += [{'header': 'Scheduled'}] + previously_scheduled

        return formatted_conditions

    def displayable_jobs(self):
        exclude_columns = [
            'Condition ID',
            'Topic Document URL',
            'Lookback Interval',
            'Subject Template',
            'Html Template',
            'Workbook ID',
            'Scheduled'
        ]
        return self.jobs[self.jobs['Scheduled'] == True].replace("", float("NaN")).drop(
            columns=exclude_columns).dropna(axis='columns', how='all')

    # In some cases, a template will need to be adjusted before sending it to the notifier.
    # For example, the Topic Document URL is an optional job parameter, so if a user doesn't
    # provide it, the HTML should not include the associated element.
    def soup_up_html_template(self):
        condition_id = self.jobs.loc[self.selected_condition]['Condition ID']
        soup = BeautifulSoup(self.app.tabs.templates_tab_content.html, 'html.parser')
        for sauce in soup.find_all(attrs={'class': 'seeq-auto-update', 'id': 'usu'}):
            sauce['href'] = f'{self.unsubscriber_notebook_url}?workbookId={self.workbook_id}&conditionId={condition_id}'
        if not self.app.tabs.scheduling_tab_content.topic_url.strip():
            for sauce in soup.find_all(attrs={'class': 'seeq-auto-update', 'id': 'tdu'}):
                sauce.replace_with('')
        return soup.prettify()

    def set_conditions(self):
        displayable_conditions = self.displayable_conditions()
        displayable_selected_condition = next(filter(lambda row: 'header' not in row, displayable_conditions), None)
        self.selected_condition = displayable_selected_condition['value'] if displayable_selected_condition else None

        self.app.condition.condition_value = self.selected_condition
        self.app.condition.condition_items = displayable_conditions

    def set_data_table(self):
        displayable_jobs = self.displayable_jobs()
        headers = [{'text': header, 'value': header} for header in displayable_jobs.keys()]
        self.app.tabs.jobs_tab_content.data_table_headers = headers
        self.app.tabs.jobs_tab_content.data_table_items = displayable_jobs.to_dict('records')

    def handle_selection_change(self, data):
        self.set_selected_job_from_models(data)
        self.selected_condition = data
        self.set_models_from_selected_job()

    def set_selected_job_from_models(self, data):
        if not self.selected_condition or self.selected_condition == data:
            return
        self.jobs.loc[self.selected_condition, 'To'] = self.app.tabs.scheduling_tab_content.to
        self.jobs.loc[self.selected_condition, 'Cc'] = self.app.tabs.scheduling_tab_content.cc
        self.jobs.loc[self.selected_condition, 'Bcc'] = self.app.tabs.scheduling_tab_content.bcc
        self.jobs.loc[self.selected_condition, 'Schedule'] = self.app.tabs.scheduling_tab_content.schedule
        self.jobs.loc[self.selected_condition, 'Topic Document URL'] = self.app.tabs.scheduling_tab_content.topic_url
        self.jobs.loc[
            self.selected_condition, 'Lookback Interval'] = self.app.tabs.scheduling_tab_content.lookback_period
        self.jobs.loc[self.selected_condition, 'Subject Template'] = self.app.tabs.templates_tab_content.subject
        self.jobs.loc[self.selected_condition, 'Html Template'] = self.app.tabs.templates_tab_content.html
        self.jobs.loc[self.selected_condition, 'Time Zone'] = self.app.tabs.scheduling_tab_content.time_zone_value

    def set_models_from_selected_job(self):
        self.app.tabs.scheduling_tab_content.to = self.jobs.loc[self.selected_condition]['To']
        self.app.tabs.scheduling_tab_content.schedule = self.jobs.loc[self.selected_condition]['Schedule']
        self.app.tabs.scheduling_tab_content.topic_url = self.jobs.loc[self.selected_condition]['Topic Document URL']
        self.app.tabs.scheduling_tab_content.lookback_period = self.jobs.loc[self.selected_condition][
            'Lookback Interval']
        self.app.tabs.scheduling_tab_content.time_zone_value = self.jobs.loc[self.selected_condition]['Time Zone']
        self.app.tabs.scheduling_tab_content.cc = self.jobs.loc[self.selected_condition]['Cc']
        self.app.tabs.scheduling_tab_content.bcc = self.jobs.loc[self.selected_condition]['Bcc']
        self.app.tabs.templates_tab_content.subject = self.jobs.loc[self.selected_condition]['Subject Template']
        self.app.tabs.templates_tab_content.html = self.jobs.loc[self.selected_condition]['Html Template']
        self.app.footer.unschedule_button_disabled = not self.jobs.loc[self.selected_condition]['Scheduled']
        self.app.footer.stopped_job_warning = 'This job is not currently running.' if \
            self.jobs.loc[self.selected_condition]['Stopped'] else ''

    def send_confirmation_email(self):
        # ''.join(x.split()).split(',') results in a list of addresses with leading and trailing spaces removed
        to = ''.join(self.app.tabs.scheduling_tab_content.to.split()).split(',')
        cc = ''.join(self.app.tabs.scheduling_tab_content.cc.split()).split(',') \
            if len(self.app.tabs.scheduling_tab_content.cc) > 0 else None
        bcc = ''.join(self.app.tabs.scheduling_tab_content.bcc.split()).split(',') \
            if len(self.app.tabs.scheduling_tab_content.bcc) > 0 else None

        spy.notifications.send_email(to=to,
                                     cc=cc,
                                     bcc=bcc,
                                     subject="Seeq Condition Monitoring Notifications",
                                     content=f'You have been subscribed to receive notifications of the Seeq condition '
                                             f'"{self.jobs.loc[self.selected_condition]["Condition Name"]}" in '
                                             f'{get_seeq_url()}. If you believe this is a mistake, please contact your '
                                             f'administrator.'
                                     )

    def on_error(self, e):
        if isinstance(e, v.Html):
            message = e
        else:
            error_text = str(e.message) if hasattr(e, 'message') else str(e)
            message = f'Something went wrong: {error_text}'

        self.app.snackbar.color = 'red darken-2'
        self.app.snackbar.message = message
        self.app.snackbar.timeout = ''
        self.app.snackbar.value = True

    def on_success(self, message):
        self.app.snackbar.color = 'success'
        self.app.snackbar.message = message
        self.app.snackbar.timeout = '5000'
        self.app.snackbar.value = True

    def on_condition_select(self, data):
        self.handle_selection_change(data)

    def on_reset_templates(self, *_):
        if not self.selected_condition:
            return
        self.app.tabs.templates_tab_content.subject = self.SUBJECT_TEMPLATE_DEFAULT
        self.app.tabs.templates_tab_content.html = self.HTML_TEMPLATE_DEFAULT
        if self.app.form_validated is True:
            self.app.footer.schedule_button_disabled = False

    def on_schedule(self, *_):
        if self.app.form_validated is False:
            self.app.snackbar.color = 'error'
            self.app.snackbar.message = 'Please fix the errors above.'
            self.app.snackbar.value = True
            return

        self.app.footer.schedule_button_loading = True
        self.jobs.loc[self.selected_condition] = pd.Series(
            {
                'Condition ID': self.jobs.loc[self.selected_condition]['Condition ID'],
                'Condition Name': self.jobs.loc[self.selected_condition]['Condition Name'],
                'Schedule': self.app.tabs.scheduling_tab_content.schedule,
                'Lookback Interval': self.app.tabs.scheduling_tab_content.lookback_period,
                'Time Zone': self.app.tabs.scheduling_tab_content.time_zone_value,
                'To': self.app.tabs.scheduling_tab_content.to,
                'Cc': self.app.tabs.scheduling_tab_content.cc,
                'Bcc': self.app.tabs.scheduling_tab_content.bcc,
                'Topic Document URL': self.app.tabs.scheduling_tab_content.topic_url,
                'Subject Template': self.app.tabs.templates_tab_content.subject,
                'Html Template': self.soup_up_html_template(),
                'Workbook ID': self.workbook_id,
                'Stopped': False,
                'Scheduled': True,
                'Inception': self.jobs.loc[self.selected_condition]['Inception'] or pd.Timestamp.now('UTC').isoformat()
            },
            name=self.selected_condition
        )
        new_jobs = self.jobs[self.jobs['Scheduled'] == True].sort_index()
        try:
            spy.jobs.push(
                new_jobs,
                datalab_notebook_url=self.notifier_notebook_url,
                label=self.workbook_id,
                quiet=True
            )
            self.send_confirmation_email()
            self.app.condition.condition_items = self.displayable_conditions()
            self.set_data_table()
        except Exception as e:
            msg = str(e)
            if 'Features/DataLab/ScheduledNotebooks/Enabled' in msg and 'Forbidden' in msg:
                self.on_error(
                    'ScheduledNotebooks are not enabled.  Contact an administrator to change th '
                    'Features/DataLab/ScheduledNotebooks/Enabled setting.')
            elif 'Features/DataLab/ScheduledNotebooks/MinimumScheduleFrequency' in msg:
                self.on_error(f'The schedule {self.jobs.loc[self.selected_condition]["Schedule"]} is too frequent.'
                              f'Contact an administrator to change the '
                              f'Features/DataLab/ScheduledNotebooks/MinimumScheduleFrequency setting.')
            else:
                self.on_error(e)
            self.app.footer.schedule_button_loading = False
            return

        self.app.footer.unschedule_button_disabled = False
        self.app.footer.schedule_button_loading = False
        self.on_success('Scheduled!')

    def on_unschedule(self, *_):
        self.app.footer.unschedule_button_loading = False
        self.jobs.loc[self.selected_condition, 'Scheduled'] = False
        remaining_jobs = self.jobs[self.jobs['Scheduled'] == True].sort_index()
        try:
            if remaining_jobs.empty:
                spy.jobs.unschedule(
                    datalab_notebook_url=self.notifier_notebook_url,
                    label=self.workbook_id,
                    quiet=True
                )
            else:
                spy.jobs.push(
                    remaining_jobs,
                    datalab_notebook_url=self.notifier_notebook_url,
                    label=self.workbook_id,
                    quiet=True
                )
        except Exception as e:
            self.on_error(e)
            self.app.footer.unschedule_button_loading = False
            return

        self.set_conditions()
        self.set_data_table()
        # self.set_selected_condition()
        self.app.footer.unschedule_button_loading = False
        self.app.footer.unschedule_button_disabled = True
        self.on_success('Unscheduled!')

    def run(self):
        return self.app
