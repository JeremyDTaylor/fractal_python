# -*- coding: utf-8 -*-
from decimal import Decimal
from typing import Generator, List

import arrow
import attr
import deserialize  # type: ignore

from fractal_python.api_client import (
    ApiClient,
    arrow_or_none,
    get_paged_response,
    money_amount,
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
@deserialize.auto_snake()
@deserialize.parser("date", arrow_or_none)
class Forecast:
    id: str
    bank_id: int
    account_id: str
    date: arrow.Arrow
    source: str = attr.ib(
        validator=[
            attr.validators.instance_of(str),
            attr.validators.matches_re(SOURCES_RE),
        ]
    )
    name: str


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
class GetForecastsResponse:
    links: dict
    results: List[Forecast]


def get_forecasts(
    client: ApiClient, company_id: str, **kwargs
) -> Generator[List[Forecast], None, None]:
    r"""Get all forecasts for the company.

    :param client: Live or Sandbox API Client
    :type client: :class:`APIClient <Response>` object
    :param company_id: Identifier of the Company
    :type company_id: String
    :param bank_id: (optional) Unique identifier for the bank
    :type bank_id: Integer
    :param account_id: (optional) String Unique identifier for the bank account
    :return: :class:`Generator <Generator>` object
    :rtype: Generator[List[Forecast], None, None]
    """
    yield from get_paged_response(
        client=client,
        company_id=company_id,
        params=BANK_ACCOUNT_PARAMS,
        url=forecasts,
        cls=GetForecastsResponse,
        **kwargs
    )


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
@deserialize.parser("value_date", arrow_or_none)
@deserialize.parser("amount", money_amount)
class ForecastedTransaction:
    id: str
    bank_id: int
    account_id: str
    forecast_id: str
    value_date: arrow.Arrow
    currency: str
    amount: Decimal
    type: str = attr.ib(
        validator=[
            attr.validators.instance_of(str),
            attr.validators.matches_re(BALANCE_TYPES_RE),
        ]
    )
    merchant: str
    category: str
    reasons: str
    source: str = attr.ib(
        validator=[
            attr.validators.instance_of(str),
            attr.validators.matches_re(SOURCES_RE),
        ]
    )


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
class GetForecastedTransactionsResponse:
    links: dict
    results: List[ForecastedTransaction]


def get_forecasted_transactions(
    client: ApiClient, company_id: str, **kwargs
) -> Generator[List[ForecastedTransaction], None, None]:
    r"""
    Get all forecasted transactions linked to the provided forecast id.

    :param client: Live or Sandbox API Client
    :type client: :class:`APIClient <Response>` object
    :param company_id: Identifier of the Company
    :type company_id: String
    :param bank_id: (optional) Unique identifier for the bank
    :type bank_id: Integer
    :param account_id: (optional) String Unique identifier for the bank account
    :type account_id: String
    :param forecast_id: (optional) String Unique identifier for the forecast
    :type forecast_id: String
    :param from: (optional) datetime Returns transactions posted on or after from date
    :param to: (optional) datetime Returns transactions posted on or before to date
    :return: :class:`Generator <Generator>` object
    :rtype: Generator[List[ForecastedTransaction], None, None]
    """
    yield from get_paged_response(
        client=client,
        company_id=company_id,
        params=FORECASTED_PARAMS,
        url=transactions,
        cls=GetForecastedTransactionsResponse,
        **kwargs
    )


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
@deserialize.parser("date", arrow_or_none)
@deserialize.parser("amount", money_amount)
class ForecastedBalance:
    id: str
    bank_id: int
    account_id: str
    forecast_id: str
    date: arrow.Arrow
    currency: str
    amount: Decimal
    type: str = attr.ib(
        validator=[
            attr.validators.instance_of(str),
            attr.validators.matches_re(BALANCE_TYPES_RE),
        ]
    )
    source: str = attr.ib(
        validator=[
            attr.validators.instance_of(str),
            attr.validators.matches_re(SOURCES_RE),
        ]
    )


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
class GetForecastedBalanceResponse:
    links: dict
    results: List[ForecastedBalance]


def get_forecasted_balances(
    client: ApiClient, company_id: str, **kwargs
) -> Generator[List[ForecastedBalance], None, None]:
    r"""
    Get all forecasted balances linked to the provided forecast id.

    :param client: Live or Sandbox API Client
    :type client: :class:`APIClient <Response>` object
    :param company_id: Identifier of the Company
    :type company_id: String
    :param bank_id: (optional) Unique identifier for the bank
    :type bank_id: Integer
    :param account_id: (optional) String Unique identifier for the bank account
    :type account_id: String
    :param forecast_id: (optional) String Unique identifier for the forecast
    :type forecast_id: String
    :param from: (optional) datetime Returns transactions posted on or after from date
    :param to: (optional) datetime Returns transactions posted on or before to date
    :return: :class:`Generator <Generator>` object
    :rtype: Generator[List[ForecastedBalance], None, None]
    """
    yield from get_paged_response(
        client=client,
        company_id=company_id,
        params=FORECASTED_PARAMS,
        url=balances,
        cls=GetForecastedBalanceResponse,
        **kwargs
    )
