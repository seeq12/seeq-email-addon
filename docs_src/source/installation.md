# User Installation

## Requirements
If you want to install the **Condition Monitor Scheduler** Seeq add-on, you will need:

- Seeq Data Lab (>=R58.2)
- Seeq administrator access
- Seeq SaaS deployment (the Email service is not available for on-prem deployments)

### Note for Seeq on-prem customers
The email service that this add-on needs is not available for on-premise deployments. For on-premise deployments, an
SMTP-only Email Notification Add-On is included within the SPy documentation that comes with every DataLab project.


## Add-on installation

The latest build of the project can be found [here](https://pypi.org/project/seeq-email-condition-monitor/) as a wheel
file. The file is published as a courtesy to the user, and it does not imply any obligation for support from the
publisher.

1. Download the `Email Condition Monitor Installer.ipynb` file
   from the [latest release](https://github.com/seeq12/seeq-email-addon/releases/latest) under the `Assets` menu.
2. Create a **new** Seeq Data Lab project and upload the `Email Condition Monitor Installer.ipynb` file to the SDL
   project.
3. Open the `Email Condition Monitor Installer.ipynb` notebook and follow the instructions in there. 


