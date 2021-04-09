import json
from typing import Any, Dict, Generator, List, Optional

import arrow
import attr
import deserialize  # type: ignore
from stringcase import camelcase

from fractal_python.api_client import ApiClient, _get_paged_response

COMPANY_ENDPOINT = "/company/v2/companies"


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
class NewCompany:
    r"""New Company.

    :attr name: Name of the Company
    :type name: str
    :attr description: (Optional) description
    :type description: str
    :attr website: (Optional) url of website
    :type website: str
    :attr industry: (Optional) industry
    :type industry: str
    :attr address: (Optional) registered address
    :type address: str
    :attr external_id: (Optional) user defined id
    :type external_id: str
    :attr crn: (Optional) registration number
    :type crn: str
    """
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
    r"""Create a new company.

    :param name: name
    :param description: Optional description
    :param website:  Optional website url
    :param industry:  Optional industry
    :param address: Optional address
    :param external_id: Optional user defined id
    :param crn: Optional registration number
    :return: a new Company object
    :rtype: NewCompany
    """
    return NewCompany(name, description, website, industry, address, external_id, crn)


class _NewCompanyEncoder(json.JSONEncoder):
    def default(self, o: NewCompany) -> Dict[str, Any]:  # pylint: disable=E0202
        return {camelcase(key): value for key, value in o.__dict__.items() if value}


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
@deserialize.parser("created_at", arrow.get)
class Company(NewCompany):
    r"""An existing Company.

    :attr id: unique id of the company assigned by Fractal
    :attr created_at: when added to Fractal
    """
    id: str
    created_at: arrow.Arrow


class _CompanyEncoder(json.JSONEncoder):
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
    r"""Response to creating companies.

    :attr id: str
    :attr message: str
    :attr status: int
    """
    id: str
    message: str
    status: int


def get_companies(client: ApiClient, **kwargs) -> Generator[List[Company], None, None]:
    r"""Retrieve existing companies.

    Can be filtered by externa_id and crn.

    :param client: the client to use for the api call
    :type client: ApiClient
    :param **kwargs:  See below

    :Keyword Arguments:
        *external_id* (('str'')) Unique identifier for the bank account
        *crn* (('str')) Unique identifier for the forecast
    :yield: pages of Companies objects
    :rtype: Generator[List[Company], None, None]

    Usage::
      >>> from fractal_python import company
      >>> companies = [x for y in company.get_companies(client) for x in y]
    """
    yield from _get_paged_response(
        client=client,
        company_id=None,
        params=[
            "external_id",
            "crn",
        ],
        url=f"{COMPANY_ENDPOINT}",
        cls=Company,
        **kwargs,
    )


def get_company(client: ApiClient, company_id: str) -> Company:
    r"""Get an existing companies.

    :param client: the client to use for the api call
    :type client: ApiClient
    :param company_id: Identifier of the Company
    :type company_id: str
    :return: company matching the unique id
    :rtype: Company
    """
    response = client._call_api(
        f"{COMPANY_ENDPOINT}/{company_id}",
        "GET",
    )
    json_response = json.loads(response.text)
    return deserialize.deserialize(Company, json_response)


def create_company(
    client: ApiClient, companies: List[NewCompany]
) -> List[CreateResponse]:
    r"""Create new companies.

    :param client: the client to use for the api call
    :type client: ApiClient
    :param companies: new companies to add
    :type companies: List[NewCompany]
    :return: response from fractal with new companies
    :rtype: CreateResponse
    """
    body = json.dumps(companies, cls=_NewCompanyEncoder)
    response = client._call_api(f"{COMPANY_ENDPOINT}", "POST", body=body)
    json_response = json.loads(response.text)
    return deserialize.deserialize(List[CreateResponse], json_response)


def delete_company(client: ApiClient, company_id: str):
    r"""Delete an existing Company.

    :param client: Live or Sandbox API Client
    :type client: ApiClient
    :param company_id: Identifier of the Company
    :type company_id: str
    :raises AssertionError: When response code not 202
    """
    if not company_id.strip():
        raise AssertionError(f'Invalid company_id "{company_id}"')
    response = client._call_api(f"{COMPANY_ENDPOINT}/{company_id}", "DELETE")
    if response.status_code != 202:
        raise AssertionError(f"status_code:{response.status_code} {response.text}")


def update_company(client: ApiClient, company: Company):
    r"""Update an existing Company.

    :param client: Live or Sandbox API Client
    :type client: ApiClient
    :param company: updated company object
    :type company: Company
    :raises AssertionError: When response code not 204
    """
    body = json.dumps(company, cls=_CompanyEncoder)
    response = client._call_api(
        f"{COMPANY_ENDPOINT}/{company.id}",
        "PUT",
        body=body,
    )
    if response.status_code != 204:
        raise AssertionError(f"status_code:{response.status_code} {response.text}")
