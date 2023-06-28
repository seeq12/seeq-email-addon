This repository is a Python project that hosts Seeq Data Lab based add-ons to enable email notifications.

----

# Add-ons included

Currently, there is only one add-on on this project

## **seeq-email-condition-monitor**

This add-on monitors a Seeq condition and sends an email when the condition is triggered. This add-on is only 
available for SaaS deployments of Seeq >=R58.2. For Seeq SaaS >=60, considered using the notifications feature in 
the core Seeq product. 

### User Installation Requirements (Seeq Data Lab)

If you want to install **seeq-email-condition-monitor** as a Seeq Add-on Tool, you will need:

- Seeq Data Lab (>=R58.2)
- Seeq administrator access
- Seeq SaaS deployment (the Email service is not available for on-prem deployments)

### Note for Seeq on-prem customers
The email service that this add-on needs is not available for on-premise deployments. For on-premise deployments, an
SMTP-only Email Notification Add-On is included within the SPy documentation that comes with every DataLab project.


### User Installation (Seeq Data Lab)

The latest build of the project can be found [here](https://pypi.org/project/seeq-email-condition-monitor/) as a wheel
file. The file is published as a courtesy to the user, and it does not imply any obligation for support from the 
publisher.

1. Download the [Email Condition Monitor Installer.ipynb](Email%20Condition%20Monitor%20Installer.ipynb) 
file. 
2. Create a **new** Seeq Data Lab project and upload the `Email Condition Monitor Installer.ipynb` file to the SDL 
   project.
3. Open the `Email Condition Monitor Installer.ipynb` notebook and follow the instructions in there. 

----

# Support

Code related issues (e.g. bugs, feature requests) can be created in the
[issue tracker](https://github.com/seeq12/seeq-email-addon/issues)

Maintainer: Seeq

----

# Citation

Please cite this work as:

```shell
seeq-email-addon
Seeq Corporation, 2022
https://github.com/seeq12/seeq-email-addon
```
