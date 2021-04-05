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
