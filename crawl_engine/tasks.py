from celery import shared_task


@shared_task
def run_base_crawler(query_url, issue_id):
    """
    Should return parsed_data dictionary or raise an exception
    :param query_url:
    :param issue_id:
    :return: dict
    """
    parser_data = dict()
    parser_data["title"] = ''
    parser_data["body"] = ''
    parser_data["query_url"] = query_url
    parser_data["issue_id"] = issue_id

    return parser_data


@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)