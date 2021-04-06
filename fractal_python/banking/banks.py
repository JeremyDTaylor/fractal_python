import json
from typing import Generator, List, Optional

import arrow
import attr
import deserialize
from stringcase import camelcase

from fractal_python.api_client import ApiClient, _call_api, get_paged_response
from fractal_python.banking.api import BANKING_ENDPOINT, arrow_or_none

banks = BANKING_ENDPOINT + "/banks"
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


def retrieve_banks(client: ApiClient) -> Generator[List[Bank], None, None]:
    yield from get_paged_response(
        client=client, company_id=None, params=None, url=banks, cls=GetBanksResponse
    )


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
class CreateBankConsentResponse(object):
    signin_url: str
    consent_id: str
    bank_id: int
    type: str
    permission: str


def create_bank_consent(
    client: ApiClient, bank_id: int, redirect: str, company_id: str
) -> CreateBankConsentResponse:
    response = _call_api(
        client=client,
        url=f"{banks}/{bank_id}/{consents}",
        method="POST",
        body=json.dumps(dict(redirect=redirect)),
        company_id=company_id,
    )
    json_response = json.loads(response.text)
    bank_consent_response = deserialize.deserialize(
        CreateBankConsentResponse, json_response
    )
    return bank_consent_response


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
    url = f"{banks}/{bank_id}/{consents}"
    yield from get_paged_response(
        client=client,
        company_id=company_id,
        params=[],
        url=url,
        cls=GetBankConsentsResponse,
    )


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
        f"{banks}/{bank_id}/{consents}/{consent_id}",
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
        f"{banks}/{bank_id}/{consents}/{consent_id}",
        "DELETE",
        company_id=company_id,
    )
    assert response.status_code == 202
