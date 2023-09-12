import pandas as pd
from seeq import spy
from seeq.addons.email.common import create_logger
from ._capsule_handler import CapsuleHandler
from ._email_builder import EmailBuilder
from ._version import __version__


class Notifier:

    def __init__(self, debug_level="INFO"):
        self.logger = create_logger(self.__class__.__name__, debug_level=debug_level)
        self.logger.propagate = False
        self.logger.info(f"Initializing Notifier. Version: {__version__}")
        self.current_job = spy.jobs.pull()
        self.capsule_handler = CapsuleHandler(current_job=self.current_job)
        self.email_builder = EmailBuilder()

    def get_polling_range(self):
        lookback_microseconds = int(24 * 60 * 60 * 1000 * 1000 * float(
            self.current_job['Lookback Interval']))
        polling_range_end = pd.Timestamp('today', tz='utc')
        polling_range_start = polling_range_end - pd.Timedelta(lookback_microseconds, 'microseconds')
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
        self.logger.info(f'start sending email for condition: {self.current_job["Condition Name"]}')
        self.logger.debug(f"Inception time: {self.current_job['Inception']}")
        polling_range_start, polling_range_end = self.get_polling_range()
        self.logger.debug(f"polling time range: {polling_range_start} - {polling_range_end}")
        capsules_starting_in_lookback_interval = self.get_capsules_starting_in_lookback_interval(polling_range_start,
                                                                                                 polling_range_end)
        self.logger.debug(pretty_print_df('capsules_starting_in_lookback_interval > polling start time:',
                                          capsules_starting_in_lookback_interval))
        unsent_capsules = self.capsule_handler.get_unsent_capsules(self.capsule_handler.retrieve_sent_capsules(),
                                                                   capsules_starting_in_lookback_interval)
        self.logger.debug(pretty_print_df('unsent capsules:', unsent_capsules))
        sent_capsules = self.capsule_handler.retrieve_sent_capsules()
        self.logger.debug(pretty_print_df('sent capsules:', sent_capsules))
        try:
            emailed_capsules, exceptions = self.email_builder.send_emails(self.current_job, unsent_capsules)
            self.logger.info(f'Emails were sent successfully for {len(emailed_capsules)} capsules:')
            self.logger.info('Emailed capsules: \n\t' + f"{emailed_capsules}")
            self.logger.info(f'Send failed for {len(exceptions)} capsules:')
            self.logger.info('Exceptions: \n\t' + f"{exceptions}")
        except Exception as ex:
            emailed_capsules, exceptions = ([], [])
            self.logger.error('Something went wrong sending emails: \n\t' + str(ex))

        if emailed_capsules:
            start_list = [capsule['Capsule Start'] for capsule in emailed_capsules]
            self.logger.debug(f"start_list: {start_list}")
            newly_sent_capsules = capsules_starting_in_lookback_interval[
                capsules_starting_in_lookback_interval['Capsule Start'].isin(start_list)
            ]
            self.logger.debug(pretty_print_df('newly_sent_capsules:', newly_sent_capsules))
            sent_capsules_updated = self.capsule_handler.update_sent_capsules(sent_capsules, newly_sent_capsules,
                                                                              polling_range_start)
            self.logger.debug(pretty_print_df('sent_capsules_updated', sent_capsules_updated))
            self.capsule_handler.store_sent_capsules(sent_capsules_updated)


def pretty_print_df(message: str, df: pd.DataFrame):
    return message + '\n' + df.to_string().replace('\n', '\n\t')
