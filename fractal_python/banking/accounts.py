# -*- coding: utf-8 -*-
from decimal import Decimal
from typing import Generator, List, Optional

import arrow
import attr
import deserialize  # type: ignore

from fractal_python.api_client import (
    ApiClient,
    arrow_or_none,
    get_paged_response,
    money_amount,
)
from fractal_python.banking.api import BANKING_ENDPOINT

accounts = BANKING_ENDPOINT + "/accounts"
balances = BANKING_ENDPOINT + "/balances"
transactions = BANKING_ENDPOINT + "/transactions"

SOURCES = ("MANUALIMPORT", "OPENBANKING")
SOURCES_RE = "|".join(SOURCES)


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
class AccountInformation:

    r"""Open Banking Read/Write API Account Information such as OBReadAccount6.

    :attr schema_name: identification scheme name, in a coded form as published
    in an external list.
    :attr identification: assigned by an institution to identify an account.
    This identification is known by the account owner.
    :attr name: the name or names of the account owner(s) represented at an account
    level, as displayed by the ASPSP's online channels. Note, the account name is not
    the product name or the nickname of the account.
    :attr secondary_identification: econdary identification of the account, as assigned
    by the account servicing institution. This can be used by building societies to
    additionally identify accounts with a roll number (in addition to a sort code and
    account number combination).
    """
    scheme_name: str
    identification: str
    name: str
    secondary_identification: Optional[str]


def account_information(value: str) -> AccountInformation:
    return deserialize.deserialize(List[AccountInformation], value)


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
@deserialize.parser("account", account_information)
class BankAccount:
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


def retrieve_bank_accounts(
    client: ApiClient, company_id: str, **kwargs
) -> Generator[List[BankAccount], None, None]:
    r"""
    Retrieves pages of all connected bank accounts for a business.

    Can be filtered by providing a bank_id.

    :param client: Live or Sandbox API Client
    :type client: ApiClient
    :param company_id: Identifier of the Company
    :param **kwargs: See below

    :Keyword Arguments:
        *bank_id* (('int'')) Unique identifier for the bank
    :yield: Pages of BankAccounts
    :rtype: Generator[List[BankAccount], None, None]
    """
    yield from get_paged_response(
        client=client,
        company_id=company_id,
        params=("bank_id",),
        url=accounts,
        cls=BankAccount,
        **kwargs
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


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
@deserialize.parser("date", arrow_or_none)
@deserialize.parser("amount", money_amount)
class BankBalance:
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


def retrieve_bank_balances(
    client: ApiClient, company_id: str, **kwargs
) -> Generator[List[BankBalance], None, None]:
    r"""
    Pages of cash balances are returned for all the bank accounts that have been
    connected to the company.

    Balances can be filtered by bank_id and account_id.

    :param client: Live or Sandbox API Client
    :type client: ApiClient
    :param company_id: Identifier of the Company
    :type company_id: str
    :param **kwargs: See below

    :Keyword Arguments:
        *bank_id* (('int'')) Unique identifier for the bank
        *account_id* (('str''))  String Unique identifier for the bank account
        *from* filter transactions posted on or after from date
        *to* filter transactions posted on or before to date
    :yield: Pages of BankBalances
    :rtype: Generator[List[BankBalance], None, None]
    """
    yield from get_paged_response(
        client=client,
        company_id=company_id,
        params=["bank_id", "account_id", "from", "to"],
        url=balances,
        cls=BankBalance,
        **kwargs
    )


MERCHANT_SOURCE_TYPES = ("MODEL", "USER", "PROVIDER")
MERCHANT_SOURCE_TYPES_RE = "|".join(MERCHANT_SOURCE_TYPES)


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
class Merchant:
    id: str
    name: str
    category_code: Optional[str]
    address_line: Optional[str]
    source: str = attr.ib(
        validator=[
            attr.validators.instance_of(str),
            attr.validators.matches_re(MERCHANT_SOURCE_TYPES_RE),
        ]
    )


def merchant(value: str) -> Merchant:
    return deserialize.deserialize(Merchant, value)


CATEGORY_SOURCE_TYPES = ("MANUALIMPORT", "OPENBANKING")
CATEGORY_SOURCE_TYPES_RE = "|".join(CATEGORY_SOURCE_TYPES)


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
class Category:
    id: str
    name: str
    category_code: Optional[str]
    address_line: Optional[str]
    source: str = attr.ib(
        validator=[
            attr.validators.instance_of(str),
            attr.validators.matches_re(CATEGORY_SOURCE_TYPES_RE),
        ]
    )


def category(value: str) -> Category:
    return deserialize.deserialize(Category, value)


TRANSACTION_STATUS = ("BOOKED", "PENDING")
TRANSACTION_STATUS_RE = "|".join(TRANSACTION_STATUS)


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
@deserialize.parser("booking_date", arrow_or_none)
@deserialize.parser("value_date", arrow_or_none)
@deserialize.parser("amount", money_amount)
@deserialize.parser("merchant", merchant)
@deserialize.parser("category", category)
class BankTransaction:
    id: str
    account_id: str
    bank_id: int
    booking_date: arrow.Arrow
    value_date: arrow.Arrow
    transaction_code: Optional[str]
    transaction_sub_code: Optional[str]
    proprietary_code: Optional[str]
    proprietary_sub_code: Optional[str]
    reference: Optional[str]
    description: str
    currency: str
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
            attr.validators.matches_re(TRANSACTION_STATUS_RE),
        ]
    )
    merchant: Optional[Merchant]
    category: Optional[Category]
    external_id: str
    source: str = attr.ib(
        validator=[
            attr.validators.instance_of(str),
            attr.validators.matches_re(SOURCES_RE),
        ]
    )


def retrieve_bank_transactions(
    client: ApiClient, company_id: str, **kwargs
) -> Generator[List[BankTransaction], None, None]:
    r"""Retrieves pages of bank transactions for all the bank accounts
    connected to the company.

    Transactions can be filtered by bank_id, account_id, from and to.

    :param client: Live or Sandbox API Client
    :type client: ApiClient
    :param company_id: Identifier of the Company
    :type company_id: str
    :param **kwargs: See below

    :Keyword Arguments:
        *bank_id* (('int'')) Unique identifier for the bank
        *account_id* (('str''))  String Unique identifier for the bank account
        *from* filter transactions posted on or after from date
        *to* filter transactions posted on or before to date
    :yield: Pages of BankTransactions
    :rtype: Generator[List[BankTransaction], None, None]
    """
    yield from get_paged_response(
        client=client,
        company_id=company_id,
        params=[
            "bank_id",
            "account_id",
            "from",
            "to",
        ],
        url=transactions,
        cls=BankTransaction,
        **kwargs
    )
