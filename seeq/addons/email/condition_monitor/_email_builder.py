import json
import re
from collections import namedtuple
import pytz
from seeq import spy


class EmailBuilder:

    def __init__(self):
        pass

    @staticmethod
    def fill_in_template(template, capsule, job):
        # The template should have substitution fields like {capsule["Some Property"]},
        # which will be replaced by the associated property if possible
        capsule_substitutions = set(re.findall(r'({capsule\[\"(.*?)\"\]})', template))
        job_substitutions = set(re.findall(r'({job\[\"(.*?)\"\]})', template))
        for to_replace, prop in capsule_substitutions:
            replacement = str(capsule[prop]) if prop in capsule else '{Capsule property not found}'
            if prop in ['Capsule Start', 'Capsule End']:
                replacement = capsule[prop].astimezone(pytz.timezone(job['Time Zone'])).isoformat()
            template = template.replace(to_replace, replacement)
        for to_replace, prop in job_substitutions:
            replacement = str(job[prop]) if prop in job else '{Job property not found}'
            template = template.replace(to_replace, replacement)
        return template

    def build_email(self, job, capsule):
        msg = {}

        html_content = self.fill_in_template(job['Html Template'], capsule, job)

        msg['subject'] = self.fill_in_template(job['Subject Template'], capsule, job)
        msg['to_emails'] = ''.join(job['To'].split()).split(',')
        if job['Cc'] != '':
            msg['cc_emails'] = ''.join(job['Cc'].split()).split(',')
        if job['Bcc'] != '':
            msg['bcc_emails'] = ''.join(job['Bcc'].split()).split(',')
        msg['content'] = html_content

        # Here one could add support for inserting inline content in the template based on a dictionary of content IDs
        # and associated file paths specified by job_details['Inline Content'].  This would be intended for static
        # content that the admin/configurer of the Notifications would set up in advance, probably setting the
        # default value in the form for the Add-on Tool.

        # soup = BeautifulSoup(html_content, 'html.parser')
        # text_content = ' '.join([text for text in soup.find_all(text=True)])

        return msg

    @staticmethod
    def build_request(msg):
        payload = json.dumps(msg)
        headers = {
            'Content-Type': 'application/json'
        }

        email_request = namedtuple("request", ["payload", "headers"])

        return email_request(payload, headers)

    def send_emails(self, job, unsent_capsules):
        messages_to_send = list()
        sent_capsules = list()
        exceptions = list()
        for _, capsule in unsent_capsules.iterrows():
            messages_to_send.append((capsule, self.build_email(job, capsule)))
        for capsule, message in messages_to_send:
            try:
                spy.notifications.send_email(to=message['to_emails'],
                                             cc=message['cc_emails'] if 'cc_emails' in message else None,
                                             bcc=message['bcc_emails'] if 'bcc_emails' in message else None,
                                             subject=message['subject'],
                                             content=message['content'],
                                             session=spy.session
                                             )

                sent_capsules.append(capsule)
            except Exception as ex:
                exceptions.append((capsule, ex))
        return sent_capsules, exceptions
