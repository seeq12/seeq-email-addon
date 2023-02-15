from datetime import datetime, timedelta
import pandas as pd
import pytz
from seeq import spy
from ._capsule_handler import CapsuleHandler
from ._email_builder import EmailBuilder


class Notifier:

    def __init__(self):
        self.current_job = spy.jobs.pull()
        self.capsule_handler = CapsuleHandler(current_job=self.current_job)
        self.email_builder = EmailBuilder()

    def get_polling_range(self):
        lookback_microseconds = int(24 * 60 * 60 * 1000 * 1000 * float(
            self.current_job['Lookback Interval']))
        polling_range_end = pd.Timestamp('today', tz='utc')
        polling_range_start = (polling_range_end - pd.Timedelta(lookback_microseconds, 'microseconds'))
        inception = pd.Timestamp(self.current_job['Inception'])
        if inception > polling_range_start:
            polling_range_start = inception
        return polling_range_start, polling_range_end

    def get_capsules_starting_in_lookback_interval(self, polling_range_start, polling_range_end):
        # ID is used to ensure only one Condition in results
        condition = spy.search({'ID': self.current_job['Condition ID']})

        capsules_starting_in_lookback_interval = spy.pull(condition, start=polling_range_start, end=polling_range_end,
                                                          tz_convert='UTC')
        if capsules_starting_in_lookback_interval.empty or \
                'Capsule Start' not in capsules_starting_in_lookback_interval:
            capsules_starting_in_lookback_interval = pd.DataFrame()
        else:
            capsules_starting_in_lookback_interval = capsules_starting_in_lookback_interval[
                capsules_starting_in_lookback_interval['Capsule Start'] > polling_range_start
                ]
        return capsules_starting_in_lookback_interval

    def send_email(self):
        polling_range_start, polling_range_end = self.get_polling_range()
        capsules_starting_in_lookback_interval = self.get_capsules_starting_in_lookback_interval(polling_range_start,
                                                                                                 polling_range_end)
        unsent_capsules = self.capsule_handler.get_unsent_capsules(self.capsule_handler.retrieve_sent_capsules(),
                                                                   capsules_starting_in_lookback_interval)
        sent_capsules = self.capsule_handler.retrieve_sent_capsules()
        try:
            emailed_capsules, exceptions = self.email_builder.send_emails(self.current_job, unsent_capsules)
            print(f'Emails were sent successfully for {len(emailed_capsules)} capsules:')
            print(emailed_capsules)
            print(f'Send failed for {len(exceptions)} capsules:')
            print(exceptions)
        except Exception as ex:
            emailed_capsules, exceptions = ([], [])
            print(f'Something went wrong sending emails: {ex}')

        if emailed_capsules:
            start_list = [capsule['Capsule Start'] for capsule in emailed_capsules]
            newly_sent_capsules = capsules_starting_in_lookback_interval[
                capsules_starting_in_lookback_interval['Capsule Start'].isin(start_list)
            ]
            sent_capsules_updated = self.capsule_handler.update_sent_capsules(sent_capsules, newly_sent_capsules,
                                                                              polling_range_start)
            self.capsule_handler.store_sent_capsules(sent_capsules_updated)
