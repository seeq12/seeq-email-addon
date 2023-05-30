import pandas as pd
from seeq import spy
from seeq.addons.email.common import create_logger
from ._capsule_handler import CapsuleHandler
from ._email_builder import EmailBuilder


class Notifier:

    def __init__(self):
        self.logger = create_logger(self.__class__.__name__)
        self.logger.propagate = False
        self.logger.info("Initializing Notifier")
        self.current_job = spy.jobs.pull()
        self.logger.debug(f"Current job is: {self.current_job['Condition Name']}")
        self.capsule_handler = CapsuleHandler(current_job=self.current_job)
        self.email_builder = EmailBuilder()

    def get_polling_range(self):
        lookback_microseconds = int(24 * 60 * 60 * 1000 * 1000 * float(
            self.current_job['Lookback Interval']))
        self.logger.debug(f"lookback in microseconds: {lookback_microseconds}")
        polling_range_end = pd.Timestamp('today', tz='utc')
        polling_range_start = polling_range_end - pd.Timedelta(lookback_microseconds, 'microseconds')
        self.logger.debug(f"Inception time: {self.current_job['Inception']}")
        inception = pd.Timestamp(self.current_job['Inception'])
        if inception > polling_range_start:
            polling_range_start = inception
        return polling_range_start, polling_range_end

    def get_capsules_starting_in_lookback_interval(self, polling_range_start, polling_range_end):
        # ID is used to ensure only one Condition in results
        condition = spy.search({'ID': self.current_job['Condition ID']})
        self.logger.debug(f"condition: {condition}")
        capsules_starting_in_lookback_interval = spy.pull(condition, start=polling_range_start, end=polling_range_end,
                                                          tz_convert='UTC')
        self.logger.debug(f'capsules_starting_in_lookback_interval: {capsules_starting_in_lookback_interval}')
        if capsules_starting_in_lookback_interval.empty or \
                'Capsule Start' not in capsules_starting_in_lookback_interval:
            capsules_starting_in_lookback_interval = pd.DataFrame()
        else:
            capsules_starting_in_lookback_interval = capsules_starting_in_lookback_interval[
                capsules_starting_in_lookback_interval['Capsule Start'] > polling_range_start
                ]
        return capsules_starting_in_lookback_interval

    def send_email(self):
        self.logger.debug()
        polling_range_start, polling_range_end = self.get_polling_range()
        self.logger.debug(f"polling time range: {polling_range_start} - {polling_range_end}")
        capsules_starting_in_lookback_interval = self.get_capsules_starting_in_lookback_interval(polling_range_start,
                                                                                                 polling_range_end)
        self.logger.debug(
            f'capsules_starting_in_lookback_interval > polling start time: {capsules_starting_in_lookback_interval}')
        unsent_capsules = self.capsule_handler.get_unsent_capsules(self.capsule_handler.retrieve_sent_capsules(),
                                                                   capsules_starting_in_lookback_interval)
        self.logger.debug(f'unsent capsules: {unsent_capsules}')
        sent_capsules = self.capsule_handler.retrieve_sent_capsules()
        self.logger.debug(f'sent capsules: {sent_capsules}')
        try:
            emailed_capsules, exceptions = self.email_builder.send_emails(self.current_job, unsent_capsules)
            self.logger.info(f'Emails were sent successfully for {len(emailed_capsules)} capsules:')
            self.logger.info(emailed_capsules)
            self.logger.info(f'Send failed for {len(exceptions)} capsules:')
            self.logger.info(exceptions)
        except Exception as ex:
            emailed_capsules, exceptions = ([], [])
            self.logger.error(f'Something went wrong sending emails: {ex}')

        if emailed_capsules:
            start_list = [capsule['Capsule Start'] for capsule in emailed_capsules]
            self.logger.debug(f"start_list: {start_list}")
            newly_sent_capsules = capsules_starting_in_lookback_interval[
                capsules_starting_in_lookback_interval['Capsule Start'].isin(start_list)
            ]
            self.logger.debug(f"newly_sent_capsules: {newly_sent_capsules}")
            sent_capsules_updated = self.capsule_handler.update_sent_capsules(sent_capsules, newly_sent_capsules,
                                                                              polling_range_start)
            self.logger.debug(f"sent_capsules_updated: {sent_capsules_updated}")
            self.capsule_handler.store_sent_capsules(sent_capsules_updated)
