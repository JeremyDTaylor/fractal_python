import json
from typing import Any, Generator, List, Optional

import arrow
import attr
import deserialize  # type: ignore
import requests
from stringcase import camelcase

from fractal_python.api_client import COMPANY_ID_HEADER, ApiClient

endpoint = "/banking/v2/banks"
consents = "consents"


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
    response = client.call_api(endpoint, "GET", query_params=query_params)
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


def _call_api(
    client: ApiClient, url: str, method: str, body: str = None, company_id: str = None
) -> requests.Response:
    headers = {COMPANY_ID_HEADER: company_id} if company_id else {}
    response: requests.Response = client.call_api(
        url, method, body=body, call_headers=headers
    )
    return response


def create_bank_consent(
    client: ApiClient, bank_id: int, redirect: str, company_id: str
) -> CreateBankConsentResponse:
    response = _call_api(
        client,
        f"{endpoint}/{bank_id}/{consents}",
        "POST",
        json.dumps(dict(redirect=redirect)),
        company_id,
    )
    json_response = json.loads(response.text)
    bank_consent_response = deserialize.deserialize(
        CreateBankConsentResponse, json_response
    )
    return bank_consent_response


def arrow_or_none(value: Any):
    return arrow.get(value) if value else None


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
@deserialize.parser("expiry_date", arrow_or_none)
@deserialize.parser("date_created", arrow_or_none)
@deserialize.parser("authorised_date", arrow_or_none)
class BankConsent(object):
    company_id: str
    permission: str
    expiry_date: Optional[arrow.Arrow]
    consent_id: str
    bank_id: int
    date_created: arrow.Arrow
    authorised_date: Optional[arrow.Arrow]
    consent_type: str
    status: str


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
class GetBankConsentsResponse(object):
    links: dict
    results: List[BankConsent]


def _handle_retrieve_consents_response(response):
    json_response = json.loads(response.text)
    consents_response = deserialize.deserialize(GetBankConsentsResponse, json_response)
    next_page = consents_response.links.get("next", None)
    return consents_response, next_page


def retrieve_bank_consents(
    client: ApiClient, bank_id: int, company_id: Optional[str] = None
) -> Generator[List[BankConsent], None, None]:
    r"""
    Retrieves consents by bank id and company id

    :param client: the client to use for the api call
    :param bank_id: the id of the bank to filter on
    :param company_id: the id of the company to filter on
    :rtype: Generator[List[BankConsent], None, None]
    """
    response = _call_api(
        client, f"{endpoint}/{bank_id}/{consents}", "GET", company_id=company_id
    )
    consents_response, next_page = _handle_retrieve_consents_response(response)
    yield consents_response.results
    while next_page:
        response = client.call_url(next_page, "GET")
        consents_response, next_page = _handle_retrieve_consents_response(response)
        yield consents_response.results


def put_bank_consent(
    client: ApiClient,
    code: str,
    id_token: str,
    state: str,
    bank_id: int,
    consent_id: str,
    company_id: str,
):
    r"""
    Call this after user has been redirected back from the bank

    :param client: the client to use for the api call
    :param code: to be exchanged for access token with the bank
    :param id_token: base64 encoded JSON for verifying
    :param state: base64b encoded JSON to persist the state
    :param bank_id: the id of the bank to filter on
    :param consent_id: id returned from create_bank_consent
    :param company_id:  the id of the company
    """
    payload = {"code": code, "id_token": id_token, "state": state}
    response = _call_api(
        client,
        f"{endpoint}/{bank_id}/{consents}/{consent_id}",
        "PUT",
        body=json.dumps(payload),
        company_id=company_id,
    )
    assert response.status_code == 204


def delete_bank_consent(
    client: ApiClient,
    bank_id: int,
    consent_id: str,
    company_id: str,
):
    r"""
    Call this after user has been redirected back from the bank

    :param client: the client to use for the api call
    :param bank_id: the id of the bank to filter on
    :param consent_id: id returned from create_bank_consent
    :param company_id:  the id of the company"""
    response = _call_api(
        client,
        f"{endpoint}/{bank_id}/{consents}/{consent_id}",
        "DELETE",
        company_id=company_id,
    )
    assert response.status_code == 202
