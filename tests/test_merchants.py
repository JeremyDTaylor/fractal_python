import pytest

from fractal_python.api_client import PARTNER_ID_HEADER, ApiClient
from fractal_python.banking import retrieve_merchants
from tests.test_api_client import make_sandbox

GET_MERCHANTS = {
    "results": [
        {
            "id": "categoryId1234",
            "name": "Vitalityhealth",
            "categoryCode": "",
            "addressLine": "",
        },
        {
            "id": "categoryId2345",
            "name": "Google",
            "categoryCode": "",
            "addressLine": "",
        },
        {"id": "categoryId3456", "name": "Uber", "categoryCode": "", "addressLine": ""},
    ],
    "links": {},
}

GET_MERCHANTS_PAGED = {
    "results": [
        {"id": "categoryId3456", "name": "Lime", "categoryCode": "", "addressLine": ""}
    ],
    "links": {"next": "mock://test/banking/v2/merchants?pageId=2"},
}


@pytest.fixture()
def merchants_client(requests_mock) -> ApiClient:
    request_headers = {
        PARTNER_ID_HEADER: "sandbox-partner",
    }
    requests_mock.register_uri(
        "GET",
        "/banking/v2/merchants",
        json=GET_MERCHANTS_PAGED,
        request_headers=request_headers,
    )
    requests_mock.register_uri(
        "GET",
        "/banking/v2/merchants?pageId=2",
        json=GET_MERCHANTS,
        request_headers=request_headers,
    )
    return make_sandbox(requests_mock)


def test_retrieve_merchants(merchants_client: ApiClient):
    merchants = [
        item
        for sublist in retrieve_merchants(client=merchants_client)
        for item in sublist
    ]
    assert len(merchants) == 4
