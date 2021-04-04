from typing import Any, Dict, List

import deserialize  # type: ignore
import pytest

from fractal_python.api_client import ApiClient
from fractal_python.bank_data import (
    Bank,
    BankEncoder,
    create_bank_consent,
    new_bank,
    retrieve_banks,
)
from tests.test_api_client import make_sandbox

GET_BANKS_1_PAGE_1: Dict[str, Any] = {
    "results": [
        {
            "id": 1,
            "name": "AIB (UK) - Personal",
            "logo": "data:image/svg+xml;base64,<link>",
        },
        {"id": 2, "name": "Lloyds", "logo": "data:image/svg+xml;base64,<link>"},
        {"id": 3, "name": "Danske", "logo": "data:image/svg+xml;base64,<link>"},
        {"id": 4, "name": "HSBC", "logo": "data:image/svg+xml;base64,<link>"},
        {"id": 5, "name": "Santander", "logo": "data:image/svg+xml;base64,<link>"},
        {"id": 6, "name": "RBS", "logo": "data:image/svg+xml;base64,<link>"},
        {"id": 7, "name": "Natwest", "logo": "data:image/svg+xml;base64,<link>"},
    ],
    "links": {},
}


@pytest.fixture()
def valid_bank() -> Bank:
    return new_bank(id=7, name="Natwest", logo="data:image/svg+xml;base64,<link>")


def test_deserialize_bank(valid_bank):
    bank = deserialize.deserialize(
        Bank, {"id": 7, "name": "Natwest", "logo": "data:image/svg+xml;base64,<link>"}
    )
    assert bank == valid_bank


def test_bank_encoder(valid_bank: Bank):
    encoder = BankEncoder()
    bank = encoder.default(valid_bank)
    assert bank["id"] == valid_bank.id
    assert bank["name"] == valid_bank.name
    assert bank["logo"] == valid_bank.logo


@pytest.fixture()
def test_client(requests_mock) -> ApiClient:
    requests_mock.register_uri("GET", "/banking/v2/banks", json=GET_BANKS_1_PAGE_1)
    return make_sandbox(requests_mock)


def test_retrieve_banks_single_page(test_client: ApiClient):
    banks: List[Bank] = [
        item for sublist in retrieve_banks(test_client) for item in sublist
    ]
    assert len(banks) == len(GET_BANKS_1_PAGE_1["results"])
    for index, bank in enumerate(banks):
        expected: Dict[str, str] = GET_BANKS_1_PAGE_1["results"][index]
        assert expected["id"] == bank.id
        assert expected["logo"] == bank.logo
        assert expected["name"] == bank.name


GET_BANKS_2_PAGE_1 = {
    "results": [
        {
            "id": 10,
            "name": "J P Morgan (UK) - Personal",
            "logo": "data:image/svg+xml;base64,<link>",
        },
    ],
    "links": {"next": "mock://test/banking/v2/banks?pageId=2"},
}


@pytest.fixture()
def test_client_paged(requests_mock, test_client) -> ApiClient:
    requests_mock.register_uri("GET", "/banking/v2/banks", json=GET_BANKS_2_PAGE_1)
    requests_mock.register_uri(
        "GET", "/banking/v2/banks?pageId=2", json=GET_BANKS_1_PAGE_1
    )
    return test_client


def test_retrieve_banks_multiple_page(test_client_paged: ApiClient):
    banks = [item for sublist in retrieve_banks(test_client_paged) for item in sublist]
    assert len(banks) == 8


GET_BANK_6_CONSENT = {
    "signinUrl": "Bank's signinUrl",
    "consentId": "ConsentID123",
    "bankId": 6,
    "type": "ACCOUNT",
    "permission": "ReadAllBankData",
}


def test_create_bank_consent(requests_mock, test_client):
    requests_mock.register_uri(
        "POST", "/banking/v2/banks/6/consents", json=GET_BANK_6_CONSENT
    )
    consent = create_bank_consent(test_client, 6, "redirect")
    assert consent.bank_id == 6
    assert consent.signin_url == "Bank's signinUrl"
    assert consent.consent_id == "ConsentID123"
    assert consent.type == "ACCOUNT"
    assert consent.permission == "ReadAllBankData"
