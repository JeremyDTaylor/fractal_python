from typing import Any, Dict, List

import deserialize  # type: ignore
import pytest

from fractal_python.api_client import COMPANY_ID_HEADER, ApiClient
from fractal_python.bank_data import (
    Bank,
    BankConsent,
    BankEncoder,
    create_bank_consent,
    new_bank,
    retrieve_bank_consents,
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
    requests_mock.register_uri(
        "GET", "/banking/v2/banks/6/consents", json=GET_ALL_BANK_6_CONSENTS_2_PAGE
    )
    requests_mock.register_uri(
        "GET",
        "/banking/v2/banks/6/consents?pageId=2",
        json=GET_ALL_BANK_6_CONSENTS_1_PAGE,
    )
    return test_client


def test_retrieve_banks_multiple_page(test_client_paged: ApiClient):
    banks = [item for sublist in retrieve_banks(test_client_paged) for item in sublist]
    assert len(banks) == 8


POST_BANK_6_CONSENT = {
    "signinUrl": "Bank's signinUrl",
    "consentId": "ConsentID123",
    "bankId": 6,
    "type": "ACCOUNT",
    "permission": "ReadAllBankData",
}


def test_create_bank_consent(requests_mock, test_client):
    requests_mock.register_uri(
        "POST", "/banking/v2/banks/6/consents", json=POST_BANK_6_CONSENT
    )
    consent = create_bank_consent(test_client, 6, "redirect", "companyId")
    assert consent.bank_id == 6
    assert consent.signin_url == "Bank's signinUrl"
    assert consent.consent_id == "ConsentID123"
    assert consent.type == "ACCOUNT"
    assert consent.permission == "ReadAllBankData"


GET_ALL_BANK_6_CONSENTS_1_PAGE = {
    "results": [
        {
            "companyId": "CompanyID1234",
            "permission": "READALLBANKDATA",
            "consentId": "ConsentID12",
            "bankId": 6,
            "dateCreated": "2020-10-28T18:26:29.699Z",
            "consentType": "Account",
            "status": "AwaitingAuthorisation",
        },
        {
            "companyId": "CompanyID5678",
            "expiryDate": "2021-01-06T17:28:14.759Z",
            "permission": "READACCOUNTSDETAIL",
            "consentId": "ConsentID34",
            "bankId": 6,
            "dateCreated": "2020-10-28T18:24:28.707Z",
            "authorisedDate": "2020-10-08T17:28:14.759Z",
            "consentType": "Account",
            "status": "Authorised",
        },
        {
            "companyId": "CompanyID9878",
            "permission": "READALLBANKDATA",
            "consentId": "ConsentID98",
            "bankId": 6,
            "dateCreated": "2020-10-28T18:24:28.707Z",
            "consentType": "Account",
            "status": "Rejected",
        },
    ],
    "links": {},
}


def test_retrieve_all_bank_consents_1_page(requests_mock, test_client):
    requests_mock.register_uri(
        "GET", "/banking/v2/banks/6/consents", json=GET_ALL_BANK_6_CONSENTS_1_PAGE
    )
    consents = [
        item
        for sublist in retrieve_bank_consents(test_client, bank_id=6)
        for item in sublist
    ]
    assert len(consents) == 3


def test_retrieve_all_bank_consents_empty_page(test_client: ApiClient, requests_mock):
    requests_mock.register_uri(
        "GET", "/banking/v2/banks/6/consents", json=dict(results=[], links={})
    )
    consents = [
        item
        for sublist in retrieve_bank_consents(test_client, bank_id=6)
        for item in sublist
    ]
    assert len(consents) == 0


GET_ALL_BANK_6_CONSENTS_2_PAGE = {
    "results": [
        {
            "companyId": "CompanyID98782",
            "permission": "READALLBANKDATA",
            "consentId": "ConsentID982",
            "bankId": 6,
            "dateCreated": "2020-10-29T18:24:28.707Z",
            "consentType": "Account",
            "status": "Rejected",
        }
    ],
    "links": {"next": "mock://test/banking/v2/banks/6/consents?pageId=2"},
}


def test_retrieve_all_bank_consents_multiple_page(test_client_paged: ApiClient):
    consents = [
        item
        for sublist in retrieve_bank_consents(test_client_paged, bank_id=6)
        for item in sublist
    ]
    assert len(consents) == 4


GET_BY_ID_BANK_6_CONSENTS_1_PAGE = {
    "results": [
        {
            "companyId": "CompanyID1234",
            "permission": "READALLBANKDATA",
            "consentId": "ConsentID12",
            "bankId": 6,
            "dateCreated": "2020-10-28T18:26:29.699Z",
            "consentType": "Account",
            "status": "AwaitingAuthorisation",
        },
    ],
    "links": {},
}


@pytest.fixture()
def test_client_company_id(requests_mock) -> ApiClient:
    request_headers = {COMPANY_ID_HEADER: "CompanyID1234"}
    requests_mock.register_uri(
        "GET",
        "/banking/v2/banks/6/consents",
        request_headers=request_headers,
        json=GET_BY_ID_BANK_6_CONSENTS_1_PAGE,
    )
    return make_sandbox(requests_mock)


def test_retrieve_bank_consents_by_company_id(
    test_client_company_id: ApiClient, requests_mock
):
    company_id = "CompanyID1234"
    consents: List[BankConsent] = [
        item
        for sublist in retrieve_bank_consents(
            test_client_company_id, bank_id=6, company_id=company_id
        )
        for item in sublist
    ]
    assert len(consents) == 1
    assert consents[0].company_id == company_id
