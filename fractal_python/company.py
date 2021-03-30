import json
from typing import Any, List, Optional

import arrow
import attr
import deserialize  # type: ignore

from fractal_python.api_client import ApiClient


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
class NewCompany(object):
    name: str
    description: Optional[str]
    website: Optional[str]
    industry: Optional[str]
    address: Optional[str]
    external_id: Optional[str]


class NewCompanyEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        return {k: v for k, v in o.__dict__.items() if v}


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
@deserialize.parser("created_at", arrow.get)
class Company(NewCompany):
    id: str
    created_at: arrow.Arrow


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
class Response(object):
    id: str
    message: str
    status: int


def get_companies(client: ApiClient) -> List[Company]:
    response = client.call_api("/company/v2/companies", "GET")
    json_response = json.loads(response.text)
    return deserialize.deserialize(List[Company], json_response)


def get_company(client: ApiClient, company_id: str) -> Company:
    response = client.call_api(
        "/company/v2/companies/:companyId",
        "GET",
        path_params={":companyId": company_id},
    )
    json_response = json.loads(response.text)
    return deserialize.deserialize(Company, json_response)


def create_company(client: ApiClient, companies: List[NewCompany]) -> List[Response]:
    body = json.dumps(companies, cls=NewCompanyEncoder)
    response = client.call_api("/company/v2/companies", "POST", body=body)
    json_response = json.loads(response.text)
    return deserialize.deserialize(List[Response], json_response)
