from typing import Generator, List

import attr
import deserialize  # type: ignore

from fractal_python.api_client import ApiClient, get_paged_response
from fractal_python.banking.api import BANKING_ENDPOINT

categories = BANKING_ENDPOINT + "/categories"


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
class Category(object):
    id: str
    name: str


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
class GetCategoriesResponse(object):
    links: dict
    results: List[Category]


def retrieve_categories(client: ApiClient) -> Generator[List[Category], None, None]:
    r"""
    Retrieves pages of all thecategories that Fractal currently supports.
    Category id and the category name are returned in the response.

    :param client: Live or Sandbox API Client
    :type client: :class:`APIClient <Response>` object
    :return: :class:`Generator <Generator>` object
    :rtype: Generator[List[Category], None, None]
    """
    yield from get_paged_response(
        client=client,
        company_id=None,
        params=None,
        url=categories,
        cls=GetCategoriesResponse,
    )
