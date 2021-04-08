# -*- coding: utf-8 -*-
import json
import uuid
from typing import Any, Callable, Dict, List, Type

import deserialize  # type: ignore
import pytest

from fractal_python.api_client import COMPANY_ID_HEADER, PARTNER_ID_HEADER, ApiClient
from fractal_python.banking import (
    Bank,
    BankConsent,
    accounts,
    balances,
    banks_endpoint,
    consents,
    create_bank_consent,
    delete_bank_consent,
    new_bank,
    put_bank_consent,
    retrieve_bank_accounts,
    retrieve_bank_balances,
    retrieve_bank_consents,
    retrieve_bank_transactions,
    retrieve_banks,
    transactions,
)
from fractal_python.banking.accounts import BankAccount, BankBalance, BankTransaction
from tests.test_api_client import TOKEN_RESPONSE

TEST_BASE_URL = "http://test"
TEST_AUTH_URL = "http://auth"
ACCOUNTS_ENDPOINT = f"{TEST_BASE_URL}{accounts}"
BALANCES_ENDPOINT = f"{TEST_BASE_URL}{balances}"
BANKS_ENDPOINT = f"{TEST_BASE_URL}{banks_endpoint}"
TRANSACTIONS_ENDPOINT = f"{TEST_BASE_URL}{transactions}"

BANK_ID = 6
COMPANY_ID = "CompanyID1234"
COMPANY_REQUEST_HEADERS = {
    COMPANY_ID_HEADER: COMPANY_ID,
    PARTNER_ID_HEADER: "sandbox-partner",
}
ACCOUNTS_PAGE_1_NEXT_URL = f"{ACCOUNTS_ENDPOINT}?pageId=2"
BALANCES_PAGE_1_NEXT_URL = f"{BALANCES_ENDPOINT}?bankId={BANK_ID}&pageId=2"
BANKS_PAGE_1_NEXT_URL = f"{BANKS_ENDPOINT}?pageId=2"
CONSENTS_PAGE_1_NEXT_URL = f"{BANKS_ENDPOINT}/{BANK_ID}/{consents}?pageId=2"
TRANSACTIONS_PAGE_1_NEXT_URL = f"{TRANSACTIONS_ENDPOINT}?bankId={BANK_ID}&pageId=2"

BANKS_1_PAGE_1: Dict[str, Any] = {
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
    return new_bank(bank_id=7, name="Natwest", logo="data:image/svg+xml;base64,<link>")


def test_deserialize_bank(valid_bank: Bank):
    bank = deserialize.deserialize(
        Bank, {"id": 7, "name": "Natwest", "logo": "data:image/svg+xml;base64,<link>"}
    )
    assert isinstance(bank, Bank)
    assert bank == valid_bank


@pytest.fixture()
def mock_client(requests_mock) -> ApiClient:
    requests_mock.register_uri("POST", "/token", text=json.dumps(TOKEN_RESPONSE))
    return ApiClient(
        f"{TEST_AUTH_URL}", f"{TEST_BASE_URL}", "sandbox-key", "sandbox-partner"
    )


@pytest.fixture()
def banks_client(requests_mock, mock_client) -> ApiClient:
    requests_mock.register_uri("GET", f"{BANKS_ENDPOINT}", json=BANKS_1_PAGE_1)
    return mock_client


def test_retrieve_banks_single_page(banks_client: ApiClient):
    banks: List[Bank] = [
        item for sublist in retrieve_banks(banks_client) for item in sublist
    ]
    assert len(banks) == len(BANKS_1_PAGE_1["results"])
    for index, bank in enumerate(banks):
        expected: Dict[str, str] = BANKS_1_PAGE_1["results"][index]
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
    "links": {"next": BANKS_PAGE_1_NEXT_URL},
}


@pytest.fixture()
def test_client_paged(requests_mock, mock_client) -> ApiClient:
    requests_mock.register_uri("GET", f"{BANKS_ENDPOINT}", json=GET_BANKS_2_PAGE_1)
    requests_mock.register_uri("GET", BANKS_PAGE_1_NEXT_URL, json=BANKS_1_PAGE_1)
    requests_mock.register_uri(
        "GET",
        f"{BANKS_ENDPOINT}/{BANK_ID}/{consents}",
        json=GET_ALL_BANK_CONSENTS_2_PAGE,
    )
    requests_mock.register_uri(
        "GET",
        CONSENTS_PAGE_1_NEXT_URL,
        json=GET_ALL_BANK_CONSENTS_1_PAGE,
    )
    return mock_client


def test_retrieve_banks_multiple_page(test_client_paged: ApiClient):
    _count_paged_items(
        client=test_client_paged,
        call=retrieve_banks,
        count=8,
        cls=Bank,
    )


POST_BANK_CONSENT = {
    "signinUrl": "Bank's signinUrl",
    "consentId": "ConsentID123",
    "bankId": BANK_ID,
    "type": "ACCOUNT",
    "permission": "ReadAllBankData",
}


def test_create_bank_consent(requests_mock, mock_client):
    requests_mock.register_uri(
        "POST", f"{BANKS_ENDPOINT}/{BANK_ID}/{consents}", json=POST_BANK_CONSENT
    )
    consent = create_bank_consent(mock_client, 6, "redirect", "companyId")
    assert consent.bank_id == 6
    assert consent.signin_url == "Bank's signinUrl"
    assert consent.consent_id == "ConsentID123"
    assert consent.type == "ACCOUNT"
    assert consent.permission == "ReadAllBankData"


GET_ALL_BANK_CONSENTS_1_PAGE = {
    "results": [
        {
            "companyId": COMPANY_ID,
            "permission": "READALLBANKDATA",
            "consentId": "ConsentID12",
            "bankId": BANK_ID,
            "dateCreated": "2020-10-28T18:26:29.699Z",
            "consentType": "Account",
            "status": "AwaitingAuthorisation",
        },
        {
            "companyId": "CompanyID5678",
            "expiryDate": "2021-01-06T17:28:14.759Z",
            "permission": "READACCOUNTSDETAIL",
            "consentId": "ConsentID34",
            "bankId": BANK_ID,
            "dateCreated": "2020-10-28T18:24:28.707Z",
            "authorisedDate": "2020-10-08T17:28:14.759Z",
            "consentType": "Account",
            "status": "Authorised",
        },
        {
            "companyId": "CompanyID9878",
            "permission": "READALLBANKDATA",
            "consentId": "ConsentID98",
            "bankId": BANK_ID,
            "dateCreated": "2020-10-28T18:24:28.707Z",
            "consentType": "Account",
            "status": "Rejected",
        },
    ],
    "links": {},
}


def test_retrieve_all_bank_consents_1_page(requests_mock, mock_client):
    requests_mock.register_uri(
        "GET",
        f"{BANKS_ENDPOINT}/{BANK_ID}/{consents}",
        json=GET_ALL_BANK_CONSENTS_1_PAGE,
    )
    _count_paged_items(
        client=mock_client,
        call=retrieve_bank_consents,
        count=3,
        cls=BankConsent,
        bank_id=BANK_ID,
    )


def test_retrieve_all_bank_consents_empty_page(mock_client: ApiClient, requests_mock):
    requests_mock.register_uri(
        "GET", f"{BANKS_ENDPOINT}/{BANK_ID}/{consents}", json=dict(results=[], links={})
    )
    _count_paged_items(
        client=mock_client,
        call=retrieve_bank_consents,
        count=0,
        cls=BankConsent,
        bank_id=BANK_ID,
    )


GET_ALL_BANK_CONSENTS_2_PAGE = {
    "results": [
        {
            "companyId": "CompanyID98782",
            "permission": "READALLBANKDATA",
            "consentId": "ConsentID982",
            "bankId": BANK_ID,
            "dateCreated": "2020-10-29T18:24:28.707Z",
            "consentType": "Account",
            "status": "Rejected",
        }
    ],
    "links": {"next": CONSENTS_PAGE_1_NEXT_URL},
}


def test_retrieve_all_bank_consents_multiple_page(test_client_paged: ApiClient):
    _count_paged_items(
        client=test_client_paged,
        call=retrieve_bank_consents,
        count=4,
        cls=BankConsent,
        bank_id=BANK_ID,
    )


GET_BY_ID_BANK_CONSENTS_1_PAGE = {
    "results": [
        {
            "companyId": COMPANY_ID,
            "permission": "READALLBANKDATA",
            "consentId": "ConsentID12",
            "bankId": BANK_ID,
            "dateCreated": "2020-10-28T18:26:29.699Z",
            "consentType": "Account",
            "status": "AwaitingAuthorisation",
        },
    ],
    "links": {},
}


@pytest.fixture()
def test_client_company_id(requests_mock, mock_client: ApiClient) -> ApiClient:
    requests_mock.register_uri(
        "GET",
        f"{BANKS_ENDPOINT}/{BANK_ID}/{consents}",
        request_headers=COMPANY_REQUEST_HEADERS,
        json=GET_BY_ID_BANK_CONSENTS_1_PAGE,
    )
    return mock_client


def test_retrieve_bank_consents_by_company_id(
    test_client_company_id: ApiClient, requests_mock
):
    _count_paged_items(
        client=test_client_company_id,
        call=retrieve_bank_consents,
        count=1,
        cls=BankConsent,
        company_id=COMPANY_ID,
        bank_id=BANK_ID,
    )


@pytest.fixture()
def put_consent_client(requests_mock, mock_client) -> ApiClient:
    requests_mock.register_uri(
        "PUT",
        f"{BANKS_ENDPOINT}/{BANK_ID}/{consents}/ConsentID12",
        request_headers=COMPANY_REQUEST_HEADERS,
        json=GET_BY_ID_BANK_CONSENTS_1_PAGE,
        status_code=204,
    )
    return mock_client


def test_put_bank_consent(put_consent_client):
    put_bank_consent(
        put_consent_client,
        code=str(uuid.uuid4()),
        id_token=str(uuid.uuid4()),
        state="state",
        bank_id=BANK_ID,
        consent_id="ConsentID12",
        company_id=COMPANY_ID,
    )


def test_put_bank_consent_400(put_consent_client, requests_mock):
    requests_mock.register_uri(
        "PUT", f"{BANKS_ENDPOINT}/{BANK_ID}/{consents}/Consent400", status_code=400
    )
    with pytest.raises(AssertionError):
        put_bank_consent(
            put_consent_client,
            code=str(uuid.uuid4()),
            id_token=str(uuid.uuid4()),
            state="state",
            bank_id=BANK_ID,
            consent_id="Consent400",
            company_id=COMPANY_ID,
        )


def test_put_bank_consent_404(put_consent_client, requests_mock):
    requests_mock.register_uri(
        "PUT", f"{BANKS_ENDPOINT}/{BANK_ID}/{consents}/Consent404", status_code=404
    )
    with pytest.raises(AssertionError):
        put_bank_consent(
            put_consent_client,
            code=str(uuid.uuid4()),
            id_token=str(uuid.uuid4()),
            state="state",
            bank_id=BANK_ID,
            consent_id="Consent404",
            company_id=COMPANY_ID,
        )


def test_put_bank_consent_502(put_consent_client, requests_mock):
    requests_mock.register_uri(
        "PUT", f"{BANKS_ENDPOINT}/{BANK_ID}/{consents}/Consent502", status_code=502
    )
    with pytest.raises(AssertionError):
        put_bank_consent(
            put_consent_client,
            code=str(uuid.uuid4()),
            id_token=str(uuid.uuid4()),
            state="state",
            bank_id=BANK_ID,
            consent_id="Consent502",
            company_id=COMPANY_ID,
        )


@pytest.fixture()
def delete_consent_client(requests_mock, mock_client: ApiClient) -> ApiClient:
    requests_mock.register_uri(
        "DELETE",
        f"{BANKS_ENDPOINT}/{BANK_ID}/{consents}/ConsentID12",
        request_headers=COMPANY_REQUEST_HEADERS,
        status_code=202,
    )
    return mock_client


def test_delete_bank_consent(delete_consent_client):
    delete_bank_consent(
        delete_consent_client,
        bank_id=BANK_ID,
        consent_id="ConsentID12",
        company_id=COMPANY_ID,
    )


def test_delete_bank_consent_404(delete_consent_client: ApiClient, requests_mock):
    requests_mock.register_uri(
        "DELETE", f"{BANKS_ENDPOINT}/{BANK_ID}/{consents}/Consent404", status_code=404
    )
    with pytest.raises(AssertionError):
        delete_bank_consent(
            delete_consent_client,
            bank_id=BANK_ID,
            consent_id="Consent404",
            company_id=COMPANY_ID,
        )


GET_BANK_ACCOUNTS = {
    "results": [
        {
            "id": "accountId1234",
            "bankId": BANK_ID,
            "currency": "GBP",
            "nickname": "Business Account",
            "account": [
                {
                    "schemeName": "IBAN",
                    "identification": "GBBANKIDEN1234",
                    "name": "Debit Account",
                    "secondaryIdentification": "Merrchant",
                }
            ],
            "externalId": "extenalid123",
            "source": "MANUALIMPORT",
        },
        {
            "id": "accountId5678",
            "bankId": BANK_ID,
            "currency": "GBP",
            "nickname": "Debit Account - NatWest - Demo",
            "account": [
                {
                    "schemeName": "UK.OBIE.SortCodeAccountNumber",
                    "identification": "5000004001234",
                    "name": "Debit Account - NatWest - Demo",
                    "secondaryIdentification": "",
                }
            ],
            "externalId": "",
            "source": "OPENBANKING",
        },
    ],
    "links": {},
}


@pytest.fixture()
def accounts_client(requests_mock, mock_client) -> ApiClient:
    requests_mock.register_uri(
        "GET",
        f"{ACCOUNTS_ENDPOINT}?bankId={BANK_ID}",
        json=GET_BANK_ACCOUNTS,
        request_headers=COMPANY_REQUEST_HEADERS,
    )
    return mock_client


def test_retrieve_all_bank_accounts_1_page(accounts_client):
    _count_paged_items(
        client=accounts_client,
        call=retrieve_bank_accounts,
        count=2,
        cls=BankAccount,
        company_id=COMPANY_ID,
        bank_id=BANK_ID,
    )


GET_BANK_ACCOUNTS_PAGE_1 = {
    "results": [
        {
            "id": "accountId12342",
            "bankId": BANK_ID,
            "currency": "GBP",
            "nickname": "Business Account",
            "account": [
                {
                    "schemeName": "IBAN",
                    "identification": "GBBANKIDEN1234",
                    "name": "Debit Account",
                    "secondaryIdentification": "Merrchant",
                }
            ],
            "externalId": "extenalid1232",
            "source": "MANUALIMPORT",
        },
        {
            "id": "accountId56782",
            "bankId": BANK_ID,
            "currency": "GBP",
            "nickname": "Debit Account - NatWest - Demo",
            "account": [
                {
                    "schemeName": "UK.OBIE.SortCodeAccountNumber",
                    "identification": "5000004001234",
                    "name": "Debit Account - NatWest - Demo",
                    "secondaryIdentification": "",
                }
            ],
            "externalId": "",
            "source": "OPENBANKING",
        },
    ],
    "links": {"next": ACCOUNTS_PAGE_1_NEXT_URL},
}


@pytest.fixture()
def paged_accounts_client(requests_mock, mock_client) -> ApiClient:
    requests_mock.register_uri(
        "GET",
        f"{ACCOUNTS_ENDPOINT}",
        json=GET_BANK_ACCOUNTS_PAGE_1,
        request_headers=COMPANY_REQUEST_HEADERS,
    )
    requests_mock.register_uri("GET", ACCOUNTS_PAGE_1_NEXT_URL, json=GET_BANK_ACCOUNTS)
    return mock_client


def test_retrieve_all_bank_accounts_2_pages(paged_accounts_client):
    _count_paged_items(
        client=paged_accounts_client,
        call=retrieve_bank_accounts,
        count=4,
        cls=BankAccount,
        company_id=COMPANY_ID,
        bank_id=BANK_ID,
    )


GET_BANK_BALANCES_RESPONSE = {
    "results": [
        {
            "id": "balanceId1234",
            "bankId": BANK_ID,
            "accountId": "accountId1357",
            "date": "2020-10-05T00:00Z",
            "amount": "11477.35",
            "currency": "GBP",
            "type": "CREDIT",
            "status": "INTERIMBOOKED",
            "externalId": "",
            "source": "OPENBANKING",
        },
        {
            "id": "balanceId3456",
            "bankId": 7,
            "accountId": "accountId3579",
            "date": "2020-10-04T00:00Z",
            "amount": "15647.35",
            "currency": "GBP",
            "type": "CREDIT",
            "status": "CLOSINGBOOKED",
            "externalId": "",
            "source": "OPENBANKING",
        },
        {
            "id": "balanceId9876",
            "bankId": 809,
            "accountId": "accountId0087",
            "date": "2020-10-03T00:00Z",
            "amount": "1477.35",
            "currency": "GBP",
            "type": "CREDIT",
            "status": "CLOSINGBOOKED",
            "externalId": "",
            "source": "MANUALIMPORT",
        },
    ],
    "links": {},
}

GET_BANK_BALANCES_RESPONSE_PAGED = {
    "results": [
        {
            "id": "balanceId12342",
            "bankId": BANK_ID,
            "accountId": "accountId13572",
            "date": "2020-10-05T00:00Z",
            "amount": "11477.35",
            "currency": "GBP",
            "type": "CREDIT",
            "status": "INTERIMBOOKED",
            "externalId": "",
            "source": "OPENBANKING",
        },
        {
            "id": "balanceId34562",
            "bankId": 7,
            "accountId": "accountId35792",
            "date": "2020-10-04T00:00Z",
            "amount": "15647.35",
            "currency": "GBP",
            "type": "CREDIT",
            "status": "CLOSINGBOOKED",
            "externalId": "",
            "source": "OPENBANKING",
        },
        {
            "id": "balanceId98762",
            "bankId": 809,
            "accountId": "accountId00872",
            "date": "2020-10-03T00:00Z",
            "amount": "1477.35",
            "currency": "GBP",
            "type": "CREDIT",
            "status": "CLOSINGBOOKED",
            "externalId": "",
            "source": "MANUALIMPORT",
        },
    ],
    "links": {"next": BALANCES_PAGE_1_NEXT_URL},
}


@pytest.fixture()
def balances_client(requests_mock, mock_client) -> ApiClient:
    requests_mock.register_uri(
        "GET",
        f"{BALANCES_ENDPOINT}?bankId={BANK_ID}",
        json=GET_BANK_BALANCES_RESPONSE_PAGED,
        request_headers=COMPANY_REQUEST_HEADERS,
    )
    requests_mock.register_uri(
        "GET",
        BALANCES_PAGE_1_NEXT_URL,
        json=GET_BANK_BALANCES_RESPONSE,
        request_headers=COMPANY_REQUEST_HEADERS,
    )
    return mock_client


def test_retrieve_bank_balances(balances_client: ApiClient):
    _count_paged_items(
        client=balances_client,
        call=retrieve_bank_balances,
        count=6,
        cls=BankBalance,
        company_id=COMPANY_ID,
        bank_id=BANK_ID,
    )


GET_BANK_TRANSACTIONS = {
    "results": [
        {
            "id": "transactionId1357",
            "bankId": BANK_ID,
            "accountId": "accountId5555",
            "bookingDate": "2020-10-16T00:00Z",
            "valueDate": "2020-10-16T00:00Z",
            "reference": "",
            "transactionCode": "",
            "transactionSubCode": "",
            "proprietaryCode": "",
            "proprietarySubCode": "",
            "description": "Dividends October",
            "amount": "2000.00",
            "currency": "GBP",
            "type": "CREDIT",
            "status": "BOOKED",
            "merchant": {
                "id": "merchantId579",
                "name": "Dividends",
                "categoryCode": "",
                "addressLine": "",
                "source": "BANK",
            },
            "category": {"id": "categoryID9876", "name": "Dividends", "source": "USER"},
            "externalId": "",
            "source": "MANUALIMPORT",
        },
        {
            "id": "transactionId1357",
            "bankId": 7,
            "accountId": "accountId1234",
            "bookingDate": "2020-10-16T00:00Z",
            "valueDate": "2020-10-16T00:00Z",
            "reference": "",
            "transactionCode": "",
            "transactionSubCode": "",
            "proprietaryCode": "",
            "proprietarySubCode": "",
            "description": "HMRC",
            "amount": "6200.00",
            "currency": "GBP",
            "type": "CREDIT",
            "status": "BOOKED",
            "merchant": {
                "id": "merchantId579",
                "name": "HMRC",
                "categoryCode": "",
                "addressLine": "",
                "source": "MODEL",
            },
            "category": {"id": "categoryID9876", "name": "Tax", "source": "MODEL"},
            "externalId": "",
            "source": "OPENBANKING",
        },
    ],
    "links": {},
}


GET_BANK_TRANSACTIONS_PAGED = {
    "results": [
        {
            "id": "transactionId13572",
            "bankId": BANK_ID,
            "accountId": "accountId5555",
            "bookingDate": "2020-10-16T00:00Z",
            "valueDate": "2020-10-16T00:00Z",
            "reference": "",
            "transactionCode": "",
            "transactionSubCode": "",
            "proprietaryCode": "",
            "proprietarySubCode": "",
            "description": "Dividends October",
            "amount": "2000.00",
            "currency": "GBP",
            "type": "CREDIT",
            "status": "BOOKED",
            "merchant": {
                "id": "merchantId579",
                "name": "Dividends",
                "categoryCode": "",
                "addressLine": "",
                "source": "BANK",
            },
            "category": {"id": "categoryID9876", "name": "Dividends", "source": "USER"},
            "externalId": "",
            "source": "MANUALIMPORT",
        },
        {
            "id": "transactionId13572",
            "bankId": 7,
            "accountId": "accountId1234",
            "bookingDate": "2020-10-16T00:00Z",
            "valueDate": "2020-10-16T00:00Z",
            "reference": "",
            "transactionCode": "",
            "transactionSubCode": "",
            "proprietaryCode": "",
            "proprietarySubCode": "",
            "description": "HMRC",
            "amount": "6200.00",
            "currency": "GBP",
            "type": "CREDIT",
            "status": "BOOKED",
            "merchant": {
                "id": "merchantId579",
                "name": "HMRC",
                "categoryCode": "",
                "addressLine": "",
                "source": "MODEL",
            },
            "category": {"id": "categoryID9876", "name": "Tax", "source": "MODEL"},
            "externalId": "",
            "source": "OPENBANKING",
        },
    ],
    "links": {"next": TRANSACTIONS_PAGE_1_NEXT_URL},
}


@pytest.fixture()
def transactions_client(requests_mock, mock_client) -> ApiClient:
    requests_mock.register_uri(
        "GET",
        f"{TRANSACTIONS_ENDPOINT}?bankId={BANK_ID}",
        json=GET_BANK_TRANSACTIONS_PAGED,
        request_headers=COMPANY_REQUEST_HEADERS,
    )
    requests_mock.register_uri(
        "GET",
        TRANSACTIONS_PAGE_1_NEXT_URL,
        json=GET_BANK_TRANSACTIONS,
        request_headers=COMPANY_REQUEST_HEADERS,
    )
    return mock_client


def test_retrieve_bank_transactions(transactions_client: ApiClient):
    _count_paged_items(
        client=transactions_client,
        call=retrieve_bank_transactions,
        count=4,
        cls=BankTransaction,
        company_id=COMPANY_ID,
        bank_id=BANK_ID,
    )


def _count_paged_items(
    client: ApiClient, call: Callable, count: int, cls: Type, **kwargs
):
    items = [item for sublist in call(client, **kwargs) for item in sublist]
    assert len(items) == count
    for item in items:
        assert isinstance(item, cls)
