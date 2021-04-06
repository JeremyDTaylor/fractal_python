import json
from typing import Any, Dict

import arrow
import attr
import deserialize  # type: ignore
import requests

from fractal_python.api_client import COMPANY_ID_HEADER, ApiClient

BANKING_ENDPOINT = "/banking/v2"


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
class Response(object):
    id: str
    message: str
    status: int


def _call_api(
    client: ApiClient,
    url: str,
    method: str,
    query_params: Dict[str, Any] = None,
    body: str = None,
    company_id: str = None,
) -> requests.Response:
    headers = {COMPANY_ID_HEADER: company_id} if company_id else {}
    response: requests.Response = client.call_api(
        url, method, query_params=query_params, body=body, call_headers=headers
    )
    return response


def arrow_or_none(value: Any):
    return arrow.get(value) if value else None


def _handle_get_response(response, cls):
    json_response = json.loads(response.text)
    response = deserialize.deserialize(cls, json_response)
    next_page = response.links.get("next", None)
    return response, next_page


def get_paged_response(client, company_id, query_params, url, cls):
    response = _call_api(
        client=client,
        url=url,
        method="GET",
        query_params=query_params,
        company_id=company_id,
    )
    headers = {COMPANY_ID_HEADER: company_id} if company_id else {}
    paged_response, next_page = _handle_get_response(response, cls)
    yield paged_response.results
    while next_page:
        response = client.call_url(next_page, "GET", call_headers=headers)
        paged_response, next_page = _handle_get_response(response, cls)
        yield paged_response.results
