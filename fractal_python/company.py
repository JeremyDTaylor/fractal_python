import json

import attr
import deserialize
from typing import List

import arrow


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
@deserialize.parser("created_at", arrow.get)
class Company(object):
    id: str
    name: str
    description: str
    website: str
    industry: str
    created_at: arrow.Arrow
    address: str
    external_id: str


def get_companies(client) -> List[Company]:
    response = client.call_api('/company/v2/companies', 'GET')
    json_response = json.loads(response.text)
    return deserialize.deserialize(List[Company], json_response)
