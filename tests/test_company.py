import arrow
import deserialize  # type: ignore
import pytest

from fractal_python.api_client import ApiClient
from fractal_python.company import (
    Company,
    CompanyEncoder,
    NewCompany,
    NewCompanyEncoder,
    create_company,
    delete_company,
    get_companies,
    get_companies_by_crn,
    get_companies_by_external_id,
    get_company,
    new_company,
    update_company,
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
    "createdAt": "2020-10-28T15:27:15.367000+00:00",
}


def test_deserialize_company():
    company = deserialize.deserialize(Company, GET_COMPANY)
    assert company.id == GET_COMPANY["id"]
    assert company.name == GET_COMPANY["name"]
    assert company.description == GET_COMPANY["description"]
    assert company.website == GET_COMPANY["website"]
    assert company.industry == GET_COMPANY["industry"]
    assert company.address == GET_COMPANY["address"]
    assert company.external_id == GET_COMPANY["externalId"]
    assert company.crn == GET_COMPANY["crn"]
    assert company.created_at.isoformat() == GET_COMPANY["createdAt"]


@pytest.fixture()
def valid_new_company() -> NewCompany:
    return NewCompany(
        name="valid_new_company name",
        description="valid_new_company description",
        website="valid_new_company website",
        industry="valid_new_company industry",
        address="valid_new_company address",
        external_id="valid_new_company external id",
        crn="valid_new_company crn",
    )


def test_new_company_encoder(valid_new_company: NewCompany):
    encoder = NewCompanyEncoder()
    new_company = encoder.default(valid_new_company)
    assert new_company["name"] == valid_new_company.name
    assert new_company["description"] == valid_new_company.description
    assert new_company["website"] == valid_new_company.website
    assert new_company["industry"] == valid_new_company.industry
    assert new_company["address"] == valid_new_company.address
    assert new_company["externalId"] == valid_new_company.external_id
    assert new_company["crn"] == valid_new_company.crn


@pytest.fixture()
def valid_company() -> Company:
    return Company(
        id="company id",
        created_at=arrow.now(),
        name="valid_new_company name",
        description="valid_new_company description",
        website="valid_new_company website",
        industry="valid_new_company industry",
        address="valid_new_company address",
        external_id="valid_new_company external id",
        crn="valid_new_company crn",
    )


def test_company_encoder(valid_company: Company):
    encoder = CompanyEncoder()
    company = encoder.default(valid_company)
    assert company["id"] == valid_company.id
    assert company["createdAt"] == valid_company.created_at.isoformat()
    assert company["name"] == valid_company.name
    assert company["description"] == valid_company.description
    assert company["website"] == valid_company.website
    assert company["industry"] == valid_company.industry
    assert company["address"] == valid_company.address
    assert company["externalId"] == valid_company.external_id
    assert company["crn"] == valid_company.crn


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


def test_company_no_name():
    with pytest.raises(ValueError):
        new_company("")


def test_company_none_name():
    with pytest.raises(TypeError):
        new_company(None)


def test_company_whitespace_name():
    with pytest.raises(ValueError):
        new_company(" ")


def test_company_simple_nonwhitespace_name():
    new_company(" a")


def test_company_special_nonwhitespace_name():
    new_company(" ? .* \\ ")


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


def test_delete_company_success(test_client: ApiClient, requests_mock):
    requests_mock.register_uri("DELETE", "/company/v2/companies/1", status_code=202)
    delete_company(test_client, company_id="1")


def test_delete_company_404(test_client: ApiClient, requests_mock):
    requests_mock.register_uri("DELETE", "/company/v2/companies/1", status_code=404)
    with pytest.raises(AssertionError):
        delete_company(test_client, company_id="1")


@pytest.fixture()
def min_valid_company() -> Company:
    return Company(
        name="Valid Company",
        description=None,
        website=None,
        industry=None,
        address=None,
        external_id=None,
        crn=None,
        id="1",
        created_at=arrow.now(),
    )


def test_update_company(test_client: ApiClient, requests_mock, min_valid_company):
    requests_mock.register_uri("PUT", "/company/v2/companies/1", status_code=204)
    update_company(test_client, min_valid_company)


def test_update_company_error(test_client: ApiClient, requests_mock, min_valid_company):
    requests_mock.register_uri("PUT", "/company/v2/companies/1", status_code=404)
    with pytest.raises(AssertionError):
        update_company(test_client, min_valid_company)
