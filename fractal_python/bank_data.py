import json
from typing import Generator, List, Optional

import attr
import deserialize  # type: ignore
from stringcase import camelcase

from fractal_python.api_client import ApiClient


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
class Bank(object):
    id: int
    name: str
    logo: Optional[str]
    logo_url: Optional[str]


def new_bank(
    id: int,
    name: str,
    logo: str = None,
    logo_url: str = None,
) -> Bank:
    return Bank(id, name, logo, logo_url)


class BankEncoder(json.JSONEncoder):
    def default(self, o: Bank) -> dict:
        return {camelcase(k): v for k, v in o.__dict__.items() if v}


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
class GetBanksResponse(object):
    links: dict
    results: List[Bank]


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
class Response(object):
    id: str
    message: str
    status: int


def retrieve_banks(client: ApiClient, query_params=None) -> Generator:
    response = client.call_api("/banking/v2/banks", "GET", query_params=query_params)
    banks_response, next_page = _handle_get_banks_response(response)
    yield banks_response.results
    while next_page:
        response = client.call_url(next_page, "GET")
        banks_response, next_page = _handle_get_banks_response(response)
        yield banks_response.results


def _handle_get_banks_response(response):
    json_response = json.loads(response.text)
    banks_response = deserialize.deserialize(GetBanksResponse, json_response)
    next_page = banks_response.links.get("next", None)
    return banks_response, next_page


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
class CreateBankConsentResponse(object):
    signin_url: str
    consent_id: str
    bank_id: int
    type: str
    permission: str


def create_bank_consent(
    client: ApiClient, bank_id: int, redirect: str
) -> CreateBankConsentResponse:
    response = client.call_api(
        "/banking/v2/banks/:bankId/consents",
        "POST",
        path_params={":bankId": bank_id},
        body=json.dumps(dict(redirect=redirect)),
    )
    json_response = json.loads(response.text)
    bank_consent_response = deserialize.deserialize(
        CreateBankConsentResponse, json_response
    )
    return bank_consent_response
