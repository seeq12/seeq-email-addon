import logging
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, Content, Personalization
from collections import namedtuple
import azure.functions as func
import jsonschema
from jsonschema.exceptions import ValidationError

sg = SendGridAPIClient(api_key=os.environ["SgAPIKey"])


def handle_bad_request(error_msg):
    logging.error(error_msg)
    return func.HttpResponse(body=error_msg, status_code=400)


def send_email(request):
    # Wrapping the SendGrid post method, so as to be able to patch while testing. https://github.com/sendgrid/sendgrid-python/issues/293
    response = namedtuple("response", ["message", "status_code"])
    sg_response = None
    try:
        sg_response = sg.send(request)
    except Exception as e:
        # The sendgrid client throws exceptions for 400 errors rather than returning the response object as expected, so we have to catch and create 
        # our own response and status code. Assuming 400 (bad request for now)
        logging.error(f'Error sending mail to sendgrid {e}')
        return response(e,400)

    # In the case that there was not an error code, we will return the response message and status code provided by sendgrid    
    return response(sg_response.body, sg_response.status_code)


def main(req: func.HttpRequest) -> func.HttpResponse:
    
    if req.method.upper() == 'GET':
        logging.info(f'Received a test request.')
        return func.HttpResponse(body='', status_code=200)

    logging.info(f'Received a send request.')

    try:
        req_body = req.get_json()
    except (AttributeError, ValueError) as e:
        return handle_bad_request(f'Error while parsing request body: {type(e)}.')
    
    schema = {
        "type": "object",
        "properties": {
            "subject": {
                "type": "string",
                "minLength": 1
            },
            "from_email": {
                "type": "string",
                "format": "email",
                "pattern": "^\S+@\S+$"
            },
            "to_emails": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "string",
                    "format": "email",
                    "pattern": "^\S+@\S+$"
                }
            },
            "cc_emails": {
                "type": "array",
                "items": {
                    "type": "string",
                    "format": "email",
                    "pattern": "^\S+@\S+$"
                }
            },
            "bcc_emails": {
                "type": "array",
                "items": {
                    "type": "string",
                    "format": "email",
                    "pattern": "^\S+@\S+$"
                }
            },
            "content": {
                "type": "string"
            }
        },
        "required": ["subject", "from_email", "to_emails", "content"]
    }

    try:
        jsonschema.validate(req_body, schema)
    except ValidationError as e:
        return handle_bad_request(f'Error while validating request body: {e}.')

    subject = req_body['subject']
    from_email = Email(req_body['from_email'])
    content = Content("text/html", req_body['content'])
    mail = Mail(from_email, None, subject, content)

    to_emails = req_body['to_emails']
    cc_emails = []
    if 'cc_emails' in req_body:
        cc_emails = req_body['cc_emails']
    bcc_emails = []
    if 'bcc_emails' in req_body:
        bcc_emails = req_body['bcc_emails']

    recipients_list = Personalization()
    for email in to_emails:
        recipients_list.add_to(Email(email))
    for email in cc_emails:
        recipients_list.add_cc(Email(email))
    for email in bcc_emails:
        recipients_list.add_bcc(Email(email))
    mail.add_personalization(recipients_list)

    logging.info('Sending POST request to SendGrid')
    response = send_email(mail)

    logging.info(f'Sending response: {response.message}, {response.status_code}.')
    return func.HttpResponse(body=response.message, status_code=response.status_code)
