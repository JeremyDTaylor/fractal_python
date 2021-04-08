# -*- coding: utf-8 -*-
import json
from typing import Generator, List, Optional

import arrow
import attr
import deserialize

from fractal_python.api_client import (
    ApiClient,
    _arrow_or_none,
    _call_api,
    _get_paged_response,
)
from fractal_python.banking.api import BANKING_ENDPOINT

banks_endpoint = BANKING_ENDPOINT + "/banks"
consents = "consents"


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
class Bank:
    id: int
    name: str
    logo: Optional[str]
    logo_url: Optional[str]


def new_bank(
    bank_id: int,
    name: str,
    logo: str = None,
    logo_url: str = None,
) -> Bank:
    return Bank(bank_id, name, logo, logo_url)


def retrieve_banks(client: ApiClient) -> Generator[List[Bank], None, None]:
    r"""Retrieves all banks.

    :param client: the client to use for the api call
    :type client: ApiClient
    :yield: Page of Banks
    :rtype: Generator[List[Bank], None, None]
    """
    yield from _get_paged_response(
        client=client,
        company_id=None,
        params=None,
        url=banks_endpoint,
        cls=Bank,
    )


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
class CreateBankConsentResponse:
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
        url=f"{banks_endpoint}/{bank_id}/{consents}",
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
@deserialize.parser("expiry_date", _arrow_or_none)
@deserialize.parser("date_created", _arrow_or_none)
@deserialize.parser("authorised_date", _arrow_or_none)
class BankConsent:
    company_id: str
    permission: str
    expiry_date: Optional[arrow.Arrow]
    consent_id: str
    bank_id: int
    date_created: arrow.Arrow
    authorised_date: Optional[arrow.Arrow]
    consent_type: str
    status: str


def retrieve_bank_consents(
    client: ApiClient, bank_id: int, company_id: Optional[str] = None
) -> Generator[List[BankConsent], None, None]:
    r"""Retrieves consents by bank id and company id

    :param client: the client to use for the api call
    :type client: ApiClient
    :param bank_id: the id of the bank to filter on
    :type bank_id: int
    :param company_id: the id of the company to filter on, defaults to None
    :type company_id: str, optional
    :yield: Page of Bank Consents
    :rtype: Generator[List[BankConsent], None, None]
    """
    url = f"{banks_endpoint}/{bank_id}/{consents}"
    yield from _get_paged_response(
        client=client,
        company_id=company_id,
        params=[],
        url=url,
        cls=BankConsent,
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
    :type client: ApiClient
    :param code: to be exchanged for access token with the bank
    :type code: str
    :param id_token: base64 encoded JSON for verifying
    :type id_token: str
    :param state: base64b encoded JSON to persist the state
    :type state: str
    :param bank_id: the id of the bank to filter on
    :type bank_id: int
    :param consent_id: id returned from create_bank_consent
    :type consent_id: str
    :param company_id:  the id of the company
    :type company_id: str
    :raises AssertionError: When response code not 204
    """
    payload = {"code": code, "id_token": id_token, "state": state}
    response = _call_api(
        client,
        f"{banks_endpoint}/{bank_id}/{consents}/{consent_id}",
        "PUT",
        body=json.dumps(payload),
        company_id=company_id,
    )
    if response.status_code != 204:
        raise AssertionError(f"status_code:{response.status_code} {response.text}")


def delete_bank_consent(
    client: ApiClient,
    bank_id: int,
    consent_id: str,
    company_id: str,
):
    r"""
    Call this after user has been redirected back from the bank

    :param client: the client to use for the api call
    :type client: ApiClient
    :param bank_id: the id of the bank to filter on
    :type bank_id: int
    :param consent_id: id returned from create_bank_consent
    :type consent_id: str
    :param company_id:  the id of the company
    :type company_id: str
    :raises AssertionError: When response code not 202
    """
    response = _call_api(
        client,
        f"{banks_endpoint}/{bank_id}/{consents}/{consent_id}",
        "DELETE",
        company_id=company_id,
    )
    if response.status_code != 202:
        raise AssertionError(f"status_code:{response.status_code} {response.text}")
