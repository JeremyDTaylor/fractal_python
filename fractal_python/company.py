import json
from typing import Generator, List, Optional

import arrow
import attr
import deserialize  # type: ignore

from fractal_python.api_client import ApiClient


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
class NewCompany(object):
    name: str = attr.ib(
        validator=[
            attr.validators.instance_of(str),
            attr.validators.matches_re(".*\\S+.*"),
        ]
    )
    description: Optional[str]
    website: Optional[str]
    industry: Optional[str]
    address: Optional[str]
    external_id: Optional[str]
    crn: Optional[str]


def new_company(
    name: str,
    description=None,
    website=None,
    industry=None,
    address=None,
    external_id=None,
    crn=None,
) -> NewCompany:
    return NewCompany(name, description, website, industry, address, external_id, crn)


class NewCompanyEncoder(json.JSONEncoder):
    def default(self, o: NewCompany) -> dict:
        return {k: v for k, v in o.__dict__.items() if v}


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
@deserialize.parser("created_at", arrow.get)
class Company(NewCompany):
    id: str
    created_at: arrow.Arrow


class CompanyEncoder(json.JSONEncoder):
    def default(self, o: Company) -> dict:
        company = {k: v for k, v in o.__dict__.items() if v and k != "created_at"}
        company["created_at"] = o.created_at.isoformat()
        return company


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
class GetCompaniesResponse(object):
    links: dict
    results: List[Company]


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
class Response(object):
    id: str
    message: str
    status: int


def get_companies(client: ApiClient, query_params=None) -> Generator:
    response = client.call_api(
        "/company/v2/companies", "GET", query_params=query_params
    )
    companies_response, next_page = _handle_get_companies_response(response)
    yield companies_response.results
    while next_page:
        response = client.call_url(next_page, "GET")
        companies_response, next_page = _handle_get_companies_response(response)
        yield companies_response.results


def _handle_get_companies_response(response):
    json_response = json.loads(response.text)
    companies_response = deserialize.deserialize(GetCompaniesResponse, json_response)
    next_page = companies_response.links.get("next", None)
    return companies_response, next_page


def get_company(client: ApiClient, company_id: str) -> Company:
    response = client.call_api(
        "/company/v2/companies/:companyId",
        "GET",
        path_params={":companyId": company_id},
    )
    json_response = json.loads(response.text)
    return deserialize.deserialize(Company, json_response)


def get_companies_by_external_id(client: ApiClient, external_id: str) -> Generator:
    query_params = dict(externalId=external_id)
    return get_companies(client, query_params=query_params)


def get_companies_by_crn(client: ApiClient, crn: str) -> Generator:
    query_params = dict(crn=crn)
    return get_companies(client, query_params=query_params)


def create_company(client: ApiClient, companies: List[NewCompany]) -> List[Response]:
    body = json.dumps(companies, cls=NewCompanyEncoder)
    response = client.call_api("/company/v2/companies", "POST", body=body)
    json_response = json.loads(response.text)
    return deserialize.deserialize(List[Response], json_response)


def delete_company(client: ApiClient, company_id: str):
    assert company_id.strip()
    response = client.call_api(
        "/company/v2/companies/:companyId",
        "DELETE",
        path_params={":companyId": company_id},
    )
    assert response.status_code == 202


def update_company(client: ApiClient, company: Company):
    body = json.dumps(company, cls=CompanyEncoder)
    response = client.call_api(
        "/company/v2/companies/:companyId",
        "PUT",
        path_params={":companyId": company.id},
        body=body,
    )
    assert response.status_code == 204
