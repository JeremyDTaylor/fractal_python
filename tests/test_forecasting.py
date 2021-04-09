import pytest

from fractal_python.api_client import COMPANY_ID_HEADER, PARTNER_ID_HEADER, ApiClient
from fractal_python.forecasting import (
    get_forecasted_balances,
    get_forecasted_transactions,
    get_forecasts,
)
from tests.test_api_client import make_sandbox

GET_FORECASTS = {
    "results": [
        {
            "id": "forecastId1234",
            "bankId": 16,
            "accountId": "9aed0933-8e38-4571-93dd-8e775c8233e7",
            "name": "Forecast-Mar1",
            "date": "2021-03-01T09:34:00.284Z",
            "source": "MANUALIMPORT",
        },
        {
            "id": "forecastId3456",
            "bankId": 16,
            "accountId": "9aed0933-8e38-4571-93dd-8e775c8233e7",
            "name": "model_forecast_21_03_01.09:32",
            "date": "2021-03-01T09:32:39.831Z",
            "source": "MODEL",
        },
    ],
    "links": {},
}

GET_FORECASTS_PAGED = {
    "results": [
        {
            "id": "forecastId3457",
            "bankId": 16,
            "accountId": "9aed0933-8e38-4571-93dd-8e775c8233e7",
            "name": "model_forecast_21_03_01.09:32",
            "date": "2021-04-01T09:32:39.831Z",
            "source": "MODEL",
        }
    ],
    "links": {"next": "mock://test/forecasting/v2/forecasts?pageId=2"},
}


@pytest.fixture()
def forecasts_client(requests_mock) -> ApiClient:
    request_headers = {
        COMPANY_ID_HEADER: "CompanyID1234",
        PARTNER_ID_HEADER: "sandbox-partner",
    }
    requests_mock.register_uri(
        "GET",
        "/forecasting/v2/forecasts",
        json=GET_FORECASTS_PAGED,
        request_headers=request_headers,
    )
    requests_mock.register_uri(
        "GET",
        "/forecasting/v2/forecasts?pageId=2",
        json=GET_FORECASTS,
        request_headers=request_headers,
    )
    return make_sandbox(requests_mock)


def test_get_forecasts(forecasts_client: ApiClient):
    forecasts = [
        item
        for sublist in get_forecasts(
            client=forecasts_client, company_id="CompanyID1234"
        )
        for item in sublist
    ]
    assert len(forecasts) == 3


GET_FORECASTED_TRANSACTIONS_PAGED = {
    "results": [
        {
            "id": "transactionId12342",
            "forecastId": "forecastId1234",
            "bankId": 16,
            "accountId": "9aed0933-8e38-4571-93dd-8e775c8233e7",
            "valueDate": "2020-10-18T03:59Z",
            "amount": "1000.00",
            "currency": "USD",
            "type": "CREDIT",
            "merchant": "LLoyds",
            "category": "Tax",
            "reasons": "",
            "source": "MANUALIMPORT",
        },
    ],
    "links": {"next": "mock://test/forecasting/v2/transactions?pageId=2"},
}

GET_FORECASTED_TRANSACTIONS = {
    "results": [
        {
            "id": "transactionId1234",
            "forecastId": "forecastId1234",
            "bankId": 16,
            "accountId": "9aed0933-8e38-4571-93dd-8e775c8233e7",
            "valueDate": "2020-09-18T03:59Z",
            "amount": "1000.00",
            "currency": "USD",
            "type": "CREDIT",
            "merchant": "LLoyds",
            "category": "Tax",
            "reasons": "",
            "source": "MANUALIMPORT",
        },
        {
            "id": "transactionId2345",
            "forecastId": "forecastId2345",
            "bankId": 16,
            "accountId": "9aed0933-8e38-4571-93dd-8e775c8233e7",
            "valueDate": "2020-09-18T03:59Z",
            "amount": "1000.00",
            "currency": "USD",
            "type": "CREDIT",
            "merchant": "LLoyds",
            "category": "Tax",
            "reasons": "",
            "source": "MANUALIMPORT",
        },
        {
            "id": "transactionId3456",
            "forecastId": "forecastId3456",
            "bankId": 16,
            "accountId": "9aed0933-8e38-4571-93dd-8e775c8233e7",
            "valueDate": "2020-09-18T03:59Z",
            "amount": "1000.00",
            "currency": "USD",
            "type": "CREDIT",
            "merchant": "LLoyds",
            "category": "Tax",
            "reasons": "",
            "source": "MANUALIMPORT",
        },
    ],
    "links": {},
}


@pytest.fixture()
def forecasted_transactions_client(requests_mock) -> ApiClient:
    request_headers = {
        COMPANY_ID_HEADER: "CompanyID1234",
        PARTNER_ID_HEADER: "sandbox-partner",
    }
    requests_mock.register_uri(
        "GET",
        "/forecasting/v2/transactions",
        json=GET_FORECASTED_TRANSACTIONS_PAGED,
        request_headers=request_headers,
    )
    requests_mock.register_uri(
        "GET",
        "/forecasting/v2/transactions?pageId=2",
        json=GET_FORECASTED_TRANSACTIONS,
        request_headers=request_headers,
    )
    return make_sandbox(requests_mock)


def test_get_forecasted_transactions(forecasted_transactions_client: ApiClient):
    forecasted_transactions = [
        item
        for sublist in get_forecasted_transactions(
            client=forecasted_transactions_client, company_id="CompanyID1234"
        )
        for item in sublist
    ]
    assert len(forecasted_transactions) == 4


GET_FORECASTED_BALANCES_PAGED = {
    "results": [
        {
            "id": "90044386-1c09-40bf-b75f-622555da29f2",
            "bankId": 16,
            "accountId": "accountId1234",
            "forecastId": "forecastId1234",
            "date": "2020-12-30T03:59Z",
            "amount": "100002.00",
            "currency": "GBP",
            "type": "CREDIT",
            "source": "MANUALIMPORT",
        },
    ],
    "links": {"next": "mock://test/forecasting/v2/balances?pageId=2"},
}


GET_FORECASTED_BALANCES = {
    "results": [
        {
            "id": "90044386-1c09-40bf-b75f-622555da29f5",
            "bankId": 16,
            "accountId": "accountId1234",
            "forecastId": "forecastId1234",
            "date": "2020-11-30T03:59Z",
            "amount": "100000.00",
            "currency": "GBP",
            "type": "CREDIT",
            "source": "MANUALIMPORT",
        },
        {
            "id": "6cb6c2d1-5b8e-4efc-8e69-7e051a6c3820",
            "bankId": 18,
            "accountId": "accountId2345",
            "forecastId": "forecastId2345",
            "date": "2020-12-30T03:59Z",
            "amount": "110000.00",
            "currency": "GBP",
            "type": "CREDIT",
            "source": "MANUALIMPORT",
        },
    ],
    "links": {},
}


@pytest.fixture()
def forecasted_balances_client(requests_mock) -> ApiClient:
    request_headers = {
        COMPANY_ID_HEADER: "CompanyID1234",
        PARTNER_ID_HEADER: "sandbox-partner",
    }
    requests_mock.register_uri(
        "GET",
        "/forecasting/v2/balances",
        json=GET_FORECASTED_BALANCES_PAGED,
        request_headers=request_headers,
    )
    requests_mock.register_uri(
        "GET",
        "/forecasting/v2/balances?pageId=2",
        json=GET_FORECASTED_BALANCES,
        request_headers=request_headers,
    )
    return make_sandbox(requests_mock)


def test_get_forecasted_balances(forecasted_balances_client: ApiClient):
    forecasted_balances = [
        item
        for sublist in get_forecasted_balances(
            client=forecasted_balances_client, company_id="CompanyID1234"
        )
        for item in sublist
    ]
    assert len(forecasted_balances) == 3
