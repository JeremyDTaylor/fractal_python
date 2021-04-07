# -*- coding: utf-8 -*-
import pytest

from fractal_python.api_client import PARTNER_ID_HEADER, ApiClient
from fractal_python.banking import retrieve_categories
from tests.test_api_client import make_sandbox

GET_CATEGORIES = {
    "results": [
        {"id": "categoryId1234", "name": "Rent and Office"},
        {"id": "categoryId2345", "name": "Other Income"},
        {"id": "categoryId3456", "name": "Entertainment"},
        {"id": "categoryId4321", "name": "Travel and Subsistence"},
        {"id": "categoryId1357", "name": "Tax"},
        {"id": "categoryId2468", "name": "Payroll"},
        {"id": "categoryId1122", "name": "Technology"},
        {"id": "categoryId2244", "name": "Funding and Interest"},
        {"id": "categoryId5678", "name": "Miscellaneous"},
        {"id": "categoryId3355", "name": "Marketing"},
        {"id": "categoryId7788", "name": "Bank Charges and Repayments"},
        {"id": "categoryId7890", "name": "Professional Services"},
        {"id": "categoryId0123", "name": "Dividends"},
        {"id": "categoryId6543", "name": "Transfers"},
        {"id": "categoryId1010", "name": "Other Expenses"},
        {"id": "categoryId8989", "name": "Sales"},
    ],
    "links": {},
}

GET_CATEGORIES_PAGED = {
    "results": [
        {"id": "categoryId89892", "name": "Sales 2"},
    ],
    "links": {"next": "mock://test/banking/v2/categories?pageId=2"},
}


@pytest.fixture()
def categories_client(requests_mock) -> ApiClient:
    request_headers = {
        PARTNER_ID_HEADER: "sandbox-partner",
    }
    requests_mock.register_uri(
        "GET",
        "/banking/v2/categories",
        json=GET_CATEGORIES_PAGED,
        request_headers=request_headers,
    )
    requests_mock.register_uri(
        "GET",
        "/banking/v2/categories?pageId=2",
        json=GET_CATEGORIES,
        request_headers=request_headers,
    )
    return make_sandbox(requests_mock)


def test_retrieve_categories(categories_client: ApiClient):
    categories = [
        item
        for sublist in retrieve_categories(client=categories_client)
        for item in sublist
    ]
    assert len(categories) == 17
