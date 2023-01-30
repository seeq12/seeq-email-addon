from pathlib import Path
from seeq.addons.email.common import installer

CURRENT_DIR = Path(__file__).parent.resolve()
NAME = 'Condition Monitor Scheduler'
DESCRIPTION = "Data Lab Notebook-based Email Notification Scheduling tool with PDF attachment support"
ICON = "fa fa-envelope"
LINK_TYPE = "window"
WINDOW_DETAILS = "toolbar=0,location=0,scrollbars=1,statusbar=0,menubar=0,resizable=1,height=700,width=600"
SORT_KEY = "e"
REUSE_WINDOW = False

SOURCE_DEPLOYMENT_FOLDER = str(CURRENT_DIR.joinpath('deploy_notebooks'))
DEPLOYMENT_FOLDER = 'Email Condition Monitor'
DEFAULT_GROUP = ['Everyone']
DEFAULT_USERS = []

SCHEDULER_NOTEBOOK_NAME = "Condition%20Monitor%20Scheduler.ipynb"
NOTIFIER_NOTEBOOK_NAME = "Notifier.ipynb"
UNSUBSCRIBER_NOTEBOOK_NAME = "Unsubscriber.ipynb"
CONFIGURATION_SECTION = 'email function condition monitor'


def install(permissions_group: list = None, permissions_users: list = None, seeq_url: str = None):
    """
     Installs Add-on Tool in Seeq Workbench

     Parameters
     ----------
     permissions_group: list, default None
         Names of the Seeq groups that will have access to each tool. If None,
         the "Everyone" group will be used by default.
     permissions_users: list, default None
         Names of Seeq users that will have access to each tool. If None, no
         individual users will be given access to the tool.
     seeq_url: str, default None
         Based URL of the Seeq server


     Returns
     --------
     -: None
         Addon will appear as Add-on Tool(s) in Seeq
         Workbench
     """

    installer(
        permissions_group=DEFAULT_GROUP if permissions_group is None else permissions_group,
        permissions_users=DEFAULT_USERS if permissions_users is None else permissions_users,
        seeq_url=seeq_url,
        name=NAME,
        description=DESCRIPTION,
        icon=ICON,
        link_type=LINK_TYPE,
        window_details=WINDOW_DETAILS,
        sort_key=SORT_KEY,
        reuse_window=REUSE_WINDOW,
        source_deployment_folder=SOURCE_DEPLOYMENT_FOLDER,
        deployment_folder=DEPLOYMENT_FOLDER,
        default_group=DEFAULT_GROUP,
        default_users=DEFAULT_USERS,
        scheduler_notebook_name=SCHEDULER_NOTEBOOK_NAME
    )
