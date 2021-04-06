from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Generator, List, Optional

import arrow
import attr
import deserialize  # type: ignore

from fractal_python.api_client import ApiClient
from fractal_python.bank_data.api import (
    BANKING_ENDPOINT,
    arrow_or_none,
    get_paged_response,
)

accounts = BANKING_ENDPOINT + "/accounts"
balances = BANKING_ENDPOINT + "/balances"

SOURCES = ("MANUALIMPORT", "OPENBANKING")
SOURCES_RE = "|".join(SOURCES)


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
            attr.validators.matches_re(SOURCES_RE),
        ]
    )


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
class GetBankAccountsResponse(object):
    links: dict
    results: List[BankAccount]


def retrieve_bank_accounts(
    client: ApiClient, bank_id: int, company_id: str
) -> Generator[List[BankAccount], None, None]:
    url = f"{accounts}"
    query_params = {"bankId": bank_id}
    yield from get_paged_response(
        client, company_id, query_params, url, GetBankAccountsResponse
    )


BALANCE_STATUS = (
    "CLOSINGAVAILABLE",
    "CLOSINGBOOKED",
    "EXPECTED",
    "FORWARDAVAILABLE",
    "INFORMATION",
    "INTERIMAVAILABLE",
    "INTERIMBOOKED",
    "OPENINGAVAILABLE",
    "OPENINGBOOKED",
    "PREVIOUSLYCLOSEDBOOKED",
)
BALANCE_STATUS_RE = "|".join(BALANCE_STATUS)
BALANCE_TYPES = ("DEBIT", "CREDIT")
BALANCE_TYPES_RE = "|".join(BALANCE_TYPES)


def money_amount(value: Any):
    return Decimal(value).quantize(Decimal("0.01"), ROUND_HALF_UP) if value else None


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
@deserialize.parser("date", arrow_or_none)
@deserialize.parser("amount", money_amount)
class BankBalance(object):
    id: str
    account_id: str
    bank_id: int
    currency: str
    date: arrow.Arrow
    amount: Decimal
    type: str = attr.ib(
        validator=[
            attr.validators.instance_of(str),
            attr.validators.matches_re(BALANCE_TYPES_RE),
        ]
    )
    status: str = attr.ib(
        validator=[
            attr.validators.instance_of(str),
            attr.validators.matches_re(BALANCE_STATUS_RE),
        ]
    )
    external_id: str
    source: str = attr.ib(
        validator=[
            attr.validators.instance_of(str),
            attr.validators.matches_re(SOURCES_RE),
        ]
    )


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
class GetBankBalancesResponse(object):
    links: dict
    results: List[BankBalance]


def retrieve_bank_balances(
    client: ApiClient, bank_id: int, company_id: str
) -> Generator[List[BankBalance], None, None]:
    url = f"{balances}"
    query_params = {"bankId": bank_id}
    yield from get_paged_response(
        client, company_id, query_params, url, GetBankBalancesResponse
    )
