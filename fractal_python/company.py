# -*- coding: utf-8 -*-
import json
from typing import Any, Dict, Generator, List, Optional

import arrow
import attr
import deserialize  # type: ignore
from stringcase import camelcase

from fractal_python.api_client import ApiClient, get_paged_response

endpoint = "/company/v2/companies"


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
class NewCompany:
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
    def default(self, o: NewCompany) -> Dict[str, Any]:  # pylint: disable=E0202
        return {camelcase(k): v for k, v in o.__dict__.items() if v}


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
@deserialize.parser("created_at", arrow.get)
class Company(NewCompany):
    id: str
    created_at: arrow.Arrow


class CompanyEncoder(json.JSONEncoder):
    def default(self, o: Company) -> Dict[str, Any]:  # pylint: disable=E0202
        arrow_attrs = [
            x
            for x in dir(o)
            if isinstance(getattr(o, x), arrow.Arrow)
            and x[:2] != "__"
            and x[-2:] != "__"
        ]
        company = {
            camelcase(k): v for k, v in o.__dict__.items() if v and k not in arrow_attrs
        }
        for x in arrow_attrs:
            company[camelcase(x)] = getattr(o, x).isoformat()
        return company


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
class CreateResponse:
    id: str
    message: str
    status: int


def get_companies(client: ApiClient, **kwargs) -> Generator[List[Company], None, None]:
    r"""
    Retrieves consents by bank id and company id

    :param client: the client to use for the api call
    :type client: ApiClient
    :param **kwargs: See below

    :Keyword Arguments:
        *external_id* (('str'')) Unique identifier for the bank account
        *crn* (('str')) Unique identifier for the forecast
    :yield: pages of Companies objects
    :rtype: Generator[List[Company], None, None]
    """
    yield from get_paged_response(
        client=client,
        company_id=None,
        params=[
            "external_id",
            "crn",
        ],
        url=f"{endpoint}",
        cls=Company,
        **kwargs,
    )


def get_company(client: ApiClient, company_id: str) -> Company:
    response = client.call_api(
        f"{endpoint}/{company_id}",
        "GET",
    )
    json_response = json.loads(response.text)
    return deserialize.deserialize(Company, json_response)


def get_companies_by_external_id(client: ApiClient, external_id: str) -> Generator:
    return get_companies(client, external_id=external_id)


def get_companies_by_crn(client: ApiClient, crn: str) -> Generator:
    return get_companies(client, crn=crn)


def create_company(
    client: ApiClient, companies: List[NewCompany]
) -> List[CreateResponse]:
    body = json.dumps(companies, cls=NewCompanyEncoder)
    response = client.call_api(f"{endpoint}", "POST", body=body)
    json_response = json.loads(response.text)
    return deserialize.deserialize(List[CreateResponse], json_response)


def delete_company(client: ApiClient, company_id: str):
    if not company_id.strip():
        raise AssertionError(f'Invalid company_id "{company_id}"')
    response = client.call_api(f"{endpoint}/{company_id}", "DELETE")
    if response.status_code != 202:
        raise AssertionError(f"status_code:{response.status_code} {response.text}")


def update_company(client: ApiClient, company: Company):
    body = json.dumps(company, cls=CompanyEncoder)
    response = client.call_api(
        f"{endpoint}/{company.id}",
        "PUT",
        body=body,
    )
    if response.status_code != 204:
        raise AssertionError(f"status_code:{response.status_code} {response.text}")
