from pole_emploi_function import get_jobs_by_domain


def pole_emploi_lambda_handler(event, context):
    domain = event['queryStringParameters']['domain']
    creation_date_from = event['queryStringParameters']['dateFrom']
    creation_date_to = event['queryStringParameters']['dateTo']
    client_id = event['queryStringParameters']['clientId']
    client_secret = event['queryStringParameters']['clientSecret']
    response = get_jobs_by_domain(domain=domain, creation_date_from=creation_date_from,
                                  creation_date_to=creation_date_to, client_id=client_id, client_secret=client_secret)
    return response
