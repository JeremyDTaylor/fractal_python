import deserialize  # type: ignore
import pytest

from fractal_python.api_client import ApiClient
from fractal_python.company import (
    NewCompany,
    create_company,
    get_companies,
    get_companies_by_crn,
    get_companies_by_external_id,
    get_company,
)
from tests.test_api_client import make_sandbox

COMPANIES = [
    {
        "id": "c9b2d3fa-85c7-453e-a3e8-f2f7sasg06732",
        "name": "Fractal Labs",
        "description": "Engineering",
        "website": "www.fractal-labs.com",
        "industry": "Tech",
        "createdAt": "2020-05-29T20:49:15.091Z",
        "address": "27, london, IG@67",
        "externalId": "",
    },
    {
        "id": "27s8530d-194d-424a-9113-c6f56gsa72d84",
        "name": "Fractal",
        "description": "",
        "website": "www.askfractal.com",
        "industry": "Tech",
        "createdAt": "2020-05-30T11:32:08.161Z",
        "address": "27, london, IG@67",
        "externalId": "",
    },
]

RESPONSES = [
    {
        "id": "854bs5bd-b8e3-4fa9-90ec-8126asgfcf720",
        "message": "Created",
        "status": 201,
    },
    {
        "id": "234bs5bd-b8e3-4fa9-23ec-8126asggfcf720",
        "message": "Bad Request",
        "status": 400,
    },
]

GET_COMPANIES_1_PAGE_1 = {
    "results": [
        {
            "id": "CompanyID1234",
            "name": "Company name",
            "description": "Micro SME",
            "website": "www.companyname.com",
            "industry": "IT",
            "address": "London",
            "externalId": "19988-7766",
            "crn": "14455-345",
            "createdAt": "2020-10-21T12:55:09.655Z",
        }
    ],
    "links": {},
}


GET_COMPANIES_2_PAGE_1 = {
    "results": [
        {
            "id": "CompanyID1234",
            "name": "Company name",
            "description": "Micro SME",
            "website": "www.companyname.com",
            "industry": "IT",
            "address": "London",
            "externalId": "19988-7766",
            "crn": "14455-345",
            "createdAt": "2020-10-21T12:55:09.655Z",
        }
    ],
    "links": {"next": "mock://test/company/v2/companies?pageId=2"},
}


GET_COMPANY = {
    "id": "CompanyID9890",
    "name": "Company name",
    "description": "Micro SME",
    "website": "www.companyname.com",
    "industry": "IT",
    "address": "London",
    "externalId": "19988-7766",
    "crn": "14455-345",
    "createdAt": "2020-10-28T15:27:15.367Z",
}


@pytest.fixture()
def test_client(requests_mock) -> ApiClient:
    requests_mock.register_uri(
        "GET", "/company/v2/companies/CompanyID9890", json=GET_COMPANY
    )
    requests_mock.register_uri(
        "GET", "/company/v2/companies", json=GET_COMPANIES_1_PAGE_1
    )
    requests_mock.register_uri("POST", "/company/v2/companies", json=RESPONSES)
    for x in COMPANIES:
        requests_mock.register_uri(
            "GET",
            "/company/v2/companies/" + x["id"],
            json=x,
        )
    return make_sandbox(requests_mock)


@pytest.fixture()
def test_client_paged(requests_mock, test_client) -> ApiClient:
    requests_mock.register_uri(
        "GET", "/company/v2/companies", json=GET_COMPANIES_2_PAGE_1
    )
    requests_mock.register_uri(
        "GET", "/company/v2/companies?pageId=2", json=GET_COMPANIES_1_PAGE_1
    )
    return test_client


def test_get_companies_single_page(test_client: ApiClient):
    companies = [item for sublist in get_companies(test_client) for item in sublist]
    assert len(companies) == len(GET_COMPANIES_1_PAGE_1["results"])


def test_get_companies_multiple_page(test_client_paged: ApiClient):
    companies = [
        item for sublist in get_companies(test_client_paged) for item in sublist
    ]
    assert len(companies) == 2


def test_get_companies_empty_page(test_client: ApiClient, requests_mock):
    requests_mock.register_uri(
        "GET", "/company/v2/companies", json=dict(results=[], links={})
    )
    companies = [item for sublist in get_companies(test_client) for item in sublist]
    assert len(companies) == 0


def test_get_company(test_client: ApiClient):
    company = get_company(test_client, COMPANIES[0]["id"])
    assert company.name == COMPANIES[0]["name"]


def test_create_company(test_client: ApiClient):
    companies = [deserialize.deserialize(NewCompany, dict(name="test"))]
    responses = create_company(test_client, companies)
    assert responses[0].status == 201
    assert responses[1].status == 400


def test_get_company_by_external_id(test_client: ApiClient, requests_mock):
    requests_mock.register_uri(
        "GET", "/company/v2/companies", json=dict(results=[], links={})
    )
    requests_mock.register_uri(
        "GET", "/company/v2/companies?externalId=test", json=GET_COMPANIES_1_PAGE_1
    )
    companies = [
        item
        for sublist in get_companies_by_external_id(test_client, external_id="test")
        for item in sublist
    ]
    assert len(companies) == len(GET_COMPANIES_1_PAGE_1["results"])


def test_get_company_by_crn(test_client: ApiClient, requests_mock):
    requests_mock.register_uri(
        "GET", "/company/v2/companies", json=dict(results=[], links={})
    )
    requests_mock.register_uri(
        "GET", "/company/v2/companies?crn=test", json=GET_COMPANIES_1_PAGE_1
    )
    companies = [
        item
        for sublist in get_companies_by_crn(test_client, crn="test")
        for item in sublist
    ]
    assert len(companies) == len(GET_COMPANIES_1_PAGE_1["results"])
