import urllib.parse as urlparse


def get_ids_from_query_parameters(jupyter_notebook_url):
    query_parameters = urlparse.parse_qs(urlparse.urlparse(jupyter_notebook_url).query)
    workbook_id = query_parameters['workbookId'][0] if 'workbookId' in query_parameters else None
    worksheet_id = query_parameters['worksheetId'][0] if 'worksheetId' in query_parameters else None
    condition_id = query_parameters['conditionId'][0] if 'conditionId' in query_parameters else None

    return dict(workbook_id=workbook_id, worksheet_id=worksheet_id, condition_id=condition_id)
