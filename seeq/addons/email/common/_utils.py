import urllib.parse as urlparse
import logging


def get_ids_from_query_parameters(jupyter_notebook_url):
    query_parameters = urlparse.parse_qs(urlparse.urlparse(jupyter_notebook_url).query)
    workbook_id = query_parameters['workbookId'][0] if 'workbookId' in query_parameters else None
    worksheet_id = query_parameters['worksheetId'][0] if 'worksheetId' in query_parameters else None
    condition_id = query_parameters['conditionId'][0] if 'conditionId' in query_parameters else None

    return dict(workbook_id=workbook_id, worksheet_id=worksheet_id, condition_id=condition_id)


def create_logger(name: str, output_file: str = None):
    if output_file is None:
        output_file = f"{name}.log"
    # Create a custom logger
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(name)

    # Create handler
    f_handler = logging.FileHandler(output_file)

    # Create formatters and add it to handlers
    f_format = logging.Formatter('%(levelname)s %(asctime)s [%(name)s] - %(message)s')
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(f_handler)

    return logger
