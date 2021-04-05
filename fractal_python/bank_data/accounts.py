import json
from typing import Generator, List, Optional

import attr
import deserialize  # type: ignore

from fractal_python.api_client import ApiClient
from fractal_python.bank_data.api import BANKING_ENDPOINT, _call_api

accounts = BANKING_ENDPOINT + "/accounts"


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
class AccountInformation(object):
    scheme_name: str
    identification: str
    name: str
    secondary_identification: Optional[str]


def account_information(value: str) -> AccountInformation:
    return deserialize.deserialize(List[AccountInformation], value)


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
@deserialize.parser("account", account_information)
class BankAccount(object):
    id: str
    bank_id: int
    currency: str
    nickname: str
    account: List[AccountInformation]
    external_id: str
    source: str = attr.ib(
        validator=[
            attr.validators.instance_of(str),
            attr.validators.matches_re("MANUALIMPORT|OPENBANKING"),
        ]
    )


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
class GetBankAccountsResponse(object):
    links: dict
    results: List[BankAccount]


def _handle_get_accounts_response(response):
    json_response = json.loads(response.text)
    response = deserialize.deserialize(GetBankAccountsResponse, json_response)
    next_page = response.links.get("next", None)
    return response, next_page


def retrieve_bank_accounts(
    client: ApiClient, bank_id: int, company_id: str
) -> Generator[List[BankAccount], None, None]:
    response = _call_api(
        client=client,
        url=f"{accounts}",
        method="GET",
        query_params={"bankId": bank_id},
        company_id=company_id,
    )
    consents_response, next_page = _handle_get_accounts_response(response)
    yield consents_response.results
    while next_page:
        response = client.call_url(next_page, "GET")
        consents_response, next_page = _handle_get_accounts_response(response)
        yield consents_response.results
