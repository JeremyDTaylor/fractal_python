from decimal import Decimal
from typing import Generator, List

import arrow
import attr
import deserialize  # type: ignore

from fractal_python.api_client import (
    ApiClient,
    _arrow_or_none,
    _get_paged_response,
    _money_amount,
)
from fractal_python.banking.accounts import BALANCE_TYPES_RE

BANK_ACCOUNT_PARAMS = [
    "bank_id",
    "account_id",
]
DATE_PARAMS = [
    "from",
    "to",
]
FORECASTED_PARAMS = (
    BANK_ACCOUNT_PARAMS
    + [
        "forecast_id",
    ]
    + DATE_PARAMS
)

FORECASTING = "/forecasting/v2"
forecasts = "%s/forecasts" % FORECASTING
transactions = "%s/transactions" % FORECASTING
balances = "%s/balances" % FORECASTING
SOURCES = ("MODEL", "MANUALIMPORT")
SOURCES_RE = "|".join(SOURCES)


@attr.s(auto_attribs=True)
class AccountEntity:
    r"""A uniquely identifiable Account related entity.

    :attr id: unique within the bank at least identifier.
    :attr bank_id: unique id of the bank that operates the account.
    :attr account_id: account that this balance is for.
    """
    id: str
    bank_id: int
    account_id: str


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
@deserialize.parser("date", _arrow_or_none)
class Forecast(AccountEntity):
    r"""Forecast of transactions on a bank account.

    :attr date: when the forecast was made
    :attr source: source of the forecast
    :attr name: name of the forecast
    """
    date: arrow.Arrow
    source: str = attr.ib(
        validator=[
            attr.validators.instance_of(str),
            attr.validators.matches_re(SOURCES_RE),
        ]
    )
    name: str


def get_forecasts(
    client: ApiClient, company_id: str, **kwargs
) -> Generator[List[Forecast], None, None]:
    r"""Get all forecasts for the company.

    :param client: Live or Sandbox API Client
    :type client: ApiClient
    :param company_id: Identifier of the Company
    :type company_id: str
    :param **kwargs: See below

    :Keyword Arguments:
        *bank_id* (('int'')) Unique identifier for the bank
        *account_id* (('str'')) Unique identifier for the bank account
    :yield: Pages of Forecast objects
    :rtype: Generator[List[Forecast], None, None]
    """
    yield from _get_paged_response(
        client=client,
        url=forecasts,
        cls=Forecast,
        param_keys=BANK_ACCOUNT_PARAMS,
        company_id=company_id,
        **kwargs,
    )


@attr.s(auto_attribs=True)
class ForecastEntity(AccountEntity):
    r"""An identifiable forecast.

    :attr forecast_id: unique id of the forecast
    """
    forecast_id: str


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
@deserialize.parser("amount", _money_amount)
class ForecastedAmount:
    r"""Amount with currency and credit/debit.

    :attr currency: the currency of the account.
    :attr amount: decimal amount
    :attr type: either DEBIT or CREDIT
    """
    currency: str
    amount: Decimal
    type: str = attr.ib(
        validator=[
            attr.validators.instance_of(str),
            attr.validators.matches_re(BALANCE_TYPES_RE),
        ]
    )


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
@deserialize.parser("value_date", _arrow_or_none)
class ForecastedTransaction(ForecastEntity, ForecastedAmount):
    r"""Forecasted Transaction on a Bank Account.

    :attr value_date: forecast value date
    :attr currency: currency of account
    :attr amount: money amount
    :attr type: Credit or Debit
    :attr merchant: name of merchant
    :attr category: category of transaction
    :attr reasons: reasons for predicting the transaction
    :attr source: model or user
    """
    value_date: arrow.Arrow
    merchant: str
    category: str
    reasons: str
    source: str = attr.ib(
        validator=[
            attr.validators.instance_of(str),
            attr.validators.matches_re(SOURCES_RE),
        ]
    )


def get_forecasted_transactions(
    client: ApiClient, company_id: str, **kwargs
) -> Generator[List[ForecastedTransaction], None, None]:
    r"""Get all forecasted transactions linked to the provided forecast id.

    Can be filtered by bank_id, account_id, forecast_od, from and to.

    :param client: Live or Sandbox API Client
    :type client: ApiClient
    :param company_id: Identifier of the Company
    :type company_id: str
    :param **kwargs: See below

    :Keyword Arguments:
        *bank_id* (('int'')) Unique identifier for the bank
        *account_id* (('str'')) Unique identifier for the bank account
        *forecast_id* (('str')) Unique identifier for the forecast
        *from* filter transactions posted on or after from date
        *to* filter transactions posted on or before to date
    :yield: Pages of ForecastedBankTransaction objects
    :rtype: Generator[List[ForecastedTransaction], None, None]
    """
    yield from _get_paged_response(
        client=client,
        url=transactions,
        cls=ForecastedTransaction,
        param_keys=FORECASTED_PARAMS,
        company_id=company_id,
        **kwargs,
    )


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
@deserialize.parser("date", _arrow_or_none)
class ForecastedBalance(ForecastEntity, ForecastedAmount):
    r"""Forecasted Balance of a Bank Account.

    :attr date: forecast balance date
    :attr source: model or user
    """
    date: arrow.Arrow
    source: str = attr.ib(
        validator=[
            attr.validators.instance_of(str),
            attr.validators.matches_re(SOURCES_RE),
        ]
    )


def get_forecasted_balances(
    client: ApiClient, company_id: str, **kwargs
) -> Generator[List[ForecastedBalance], None, None]:
    r"""Get all forecasted balances linked to the provided forecast id.

    Can filter on bank_id, account_id, forecast_id, from and to

    :param client: Live or Sandbox API Client
    :type client: ApiClient
    :param company_id: Identifier of the Company
    :type company_id: str
    :param **kwargs: See below

    :Keyword Arguments:
        *bank_id* (('int'')) Unique identifier for the bank
        *account_id* (('str'')) Unique identifier for the bank account
        *forecast_id* (('str')) Unique identifier for the forecast
        *from* filter transactions posted on or after from date
        *to* filter transactions posted on or before to date
    :yield: pages of ForecastedBalance objects
    :rtype: Generator[List[ForecastedBalance], None, None]
    """
    yield from _get_paged_response(
        client=client,
        url=balances,
        cls=ForecastedBalance,
        param_keys=FORECASTED_PARAMS,
        company_id=company_id,
        **kwargs,
    )
