import pytest

from fractal_python.api_client import ApiClient
from fractal_python.company import get_companies, get_company
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


@pytest.fixture()
def client(requests_mock) -> ApiClient:
    requests_mock.register_uri("GET", "/company/v2/companies", json=COMPANIES)
    for x in COMPANIES:
        requests_mock.register_uri(
            "GET",
            "https://sandbox.askfractal.com/company/v2/companies/" + x["id"],
            json=x,
        )
    return make_sandbox(requests_mock)


def test_get_companies(client):
    companies = get_companies(client)
    assert len(companies) == 2


def test_get_company(client):
    company = get_company(client, COMPANIES[0]["id"])
    assert company.name == COMPANIES[0]["name"]
