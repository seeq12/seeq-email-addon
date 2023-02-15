import urllib.parse as urlparse
from seeq import spy
from seeq.spy import _url
from seeq.sdk import *
from seeq.spy import Session
from urllib.parse import urlparse, unquote
from datetime import datetime, timezone
import ipaddress
from seeq.addons.email.common import copy_folders


def parse_url(url):
    unquoted_url = unquote(url)
    return urlparse(unquoted_url)


def is_ipv4(url):
    parsed_url = parse_url(url)
    try:
        ipaddress.IPv4Network(parsed_url.hostname)
        return True
    except ValueError:
        return False


def get_seeq_url():
    if hasattr(spy.session, 'public_url'):
        if spy.session.public_url is not None:
            if not is_ipv4(spy.session.public_url):
                return spy.session.public_url

    if hasattr(spy.session, 'private_url'):
        if spy.session.private_url is not None:
            if not is_ipv4(spy.session.private_url):
                return spy.session.private_url

    return None


def install_addon(sdl_url, permissions_group, permissions_users, **kwargs):
    """
    Installs Add-on Tool in Seeq Workbench

    Parameters
    ----------
    sdl_url: str
        URL of the SDL container.
        E.g. `https://my.seeq.com/data-lab/6AB49411-917E-44CC-BA19-5EE0F903100C/`
    permissions_group: list
        Names of the Seeq groups that will have access to each tool.
    permissions_users: list
        Names of Seeq users that will have access to each tool.

    Returns
    --------
    -: None
        Addon will appear as Add-on Tool(s) in Seeq
        Workbench
    """

    name = kwargs.get('name')
    description = kwargs.get('description')
    icon = kwargs.get('icon')
    link_type = kwargs.get('link_type')
    window_details = kwargs.get('window_details')
    sort_key = kwargs.get('sort_key')
    reuse_window = kwargs.get('reuse_window')
    source_deployment_folder = kwargs.get('source_deployment_folder')
    deployment_folder = kwargs.get('deployment_folder')
    default_group = kwargs.get('default_group')
    default_users = kwargs.get('default_users')
    scheduler_notebook_name = kwargs.get('scheduler_notebook_name')

    permissions_group = permissions_group if permissions_group else default_group
    permissions_users = permissions_users if permissions_users else default_users
    add_on_details = {
        "Name": name,
        "Description": description,
        "Icon": icon,
        "Target URL": f'{sdl_url}/apps/{deployment_folder}/{scheduler_notebook_name}',
        "Link Type": link_type,
        "Window Details": window_details,
        "Sort Key": sort_key,
        "Reuse Window": reuse_window,
        "Groups": permissions_group,
        "Users": permissions_users
    }

    copy_folders(des_folder=deployment_folder, src_folder=source_deployment_folder,
                 overwrite_folder=False, overwrite_contents=True)
    spy.addons.install(add_on_details, include_workbook_parameters=True, update_tool=True, update_permissions=True)


def enable_addon_tools(session: Session, **kwargs):
    addon_tools_option_path = 'Features/AddOnTools/Enabled'
    scheduled_notebooks_option_path = 'Features/DataLab/ScheduledNotebooks/Enabled'

    system_api = SystemApi(session.client)
    configuration_output = system_api.get_configuration_options(limit=5000)
    addon_tools_already_enabled = next(option.value for option in configuration_output.configuration_options if
                                       option.path == addon_tools_option_path)
    scheduled_notebooks_already_enabled = next((option.value for option in configuration_output.configuration_options
                                                if option.path == scheduled_notebooks_option_path))

    configuration_options_update = []
    if not addon_tools_already_enabled:
        configuration_options_update.append(
            ConfigurationOptionInputV1(
                note=f'Set to true by {kwargs.get("name")} Installer user {spy.user.email} '
                     f'{datetime.now(timezone.utc)}',
                path=addon_tools_option_path,
                value=True
            )
        )

    if not scheduled_notebooks_already_enabled:
        configuration_options_update.append(
            ConfigurationOptionInputV1(
                note=f'Set to true by {kwargs.get("name")} Installer user {spy.user.email} '
                     f'{datetime.now(timezone.utc)}',
                path=scheduled_notebooks_option_path,
                value=True
            )
        )

    if configuration_options_update:
        config_options = ConfigurationInputV1(configuration_options=configuration_options_update)
        system_api.set_configuration_options(body=config_options)


def installer(permissions_group, permissions_users, seeq_url=None, **kwargs):
    if seeq_url is None:
        seeq_url = get_seeq_url()

    # let's double-check that it's not None after trying to get it.
    if seeq_url is None:
        print(f"We could not automatically find the base URL of your Seeq server.")
        seeq_url = input(f"\n Please Input Seeq base URL (eg: https://example.seeq.site): ")

    url_parsed = urlparse(seeq_url)
    seeq_url_base = f"{url_parsed.scheme}://{url_parsed.netloc}"
    project_id = spy.utils.get_data_lab_project_id()
    sdl_url = f'{seeq_url_base}/data-lab/{project_id}'

    if project_id is None:
        print("\nThe project ID could not be found. Please provide the SDL project URL with the format "
              "https://my.seeq.com/data-lab/6AB49411-917E-44CC-BA19-5EE0F903100C/\n")
        sdl_url = input("Seeq Data Lab project URL: ")
        project_id = spy.utils.get_data_lab_project_id_from_url(sdl_url)
        if not project_id:
            raise RuntimeError('Could not install addon because the SDL project ID could not be found')
    sdl_url_sanitized = _url.SeeqURL.parse(sdl_url).url

    print(f"\nThe addon will be installed on the SDL notebook: {sdl_url_sanitized}\n"
          f"If this is not your intent, you can quit the installation now (ctrl + C")
    print('\n[enter] to continue or type "quit" to exit installation')

    choice = None
    while choice != '' and choice != 'quit':
        choice = input()
        if choice == '':
            enable_addon_tools(spy.session, **kwargs)
            install_addon(sdl_url_sanitized, permissions_group=permissions_group, permissions_users=permissions_users,
                          **kwargs)
        elif choice == 'quit':
            print("\nExited installation")
        else:
            print(f'\nCommand "{choice}" is not valid')
            print('\n[enter] to continue the installation or type "quit" to exit installation')
