import os
from pathlib import Path
import pandas as pd
from seeq import spy


class CapsuleHandler:

    def __init__(self, current_job=None):

        self.sent_capsules_pickle_subfolder = Path('_Sent Capsules')
        if not os.path.exists(self.sent_capsules_pickle_subfolder):
            os.mkdir(self.sent_capsules_pickle_subfolder)

        self.current_job = spy.jobs.pull() if current_job is None else current_job
        sent_capsules_pickle_name = Path(
            f'sent_capsules_for_condition_{self.current_job["Condition ID"]}'
            f'_in_analysis_{self.current_job["Workbook ID"]}.pkl'
        )
        self.sent_capsules_pickle_path = self.sent_capsules_pickle_subfolder / sent_capsules_pickle_name

    @staticmethod
    def update_sent_capsules(sent_capsules_df, newly_sent_capsules_df, polling_range_start):
        if sent_capsules_df.empty:
            return newly_sent_capsules_df
        if newly_sent_capsules_df.empty:
            return sent_capsules_df
        updated_df = sent_capsules_df.append(newly_sent_capsules_df, ignore_index=True).drop_duplicates('Capsule Start')
        return updated_df[updated_df['Capsule Start'] > polling_range_start].sort_values(by='Capsule Start')

    @staticmethod
    def get_unsent_capsules(sent_capsules_df, pulled_capsules_df):
        if sent_capsules_df.empty or pulled_capsules_df.empty:
            return pulled_capsules_df
        return pulled_capsules_df[~pulled_capsules_df['Capsule Start'].isin(sent_capsules_df['Capsule Start'])]

    def store_sent_capsules(self, capsules_df, to_file_path=None):
        to_file_path = to_file_path if to_file_path is not None else self.sent_capsules_pickle_path
        capsules_df.to_pickle(to_file_path)

    def retrieve_sent_capsules(self, from_file_path=None):
        from_file_path = from_file_path if from_file_path is not None else self.sent_capsules_pickle_path
        if os.path.exists(from_file_path):
            return pd.read_pickle(from_file_path)
        else:
            return pd.DataFrame()
