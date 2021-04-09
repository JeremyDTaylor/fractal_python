from typing import Generator, List

import attr
import deserialize  # type: ignore

from fractal_python.api_client import ApiClient, _get_paged_response
from fractal_python.banking.api import BANKING_ENDPOINT

categories = BANKING_ENDPOINT + "/categories"


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
class Category:
    r"""Fractal Category.

    :attr id: unique identifier
    :attr name: human readable name
    """
    id: str
    name: str


def retrieve_categories(client: ApiClient) -> Generator[List[Category], None, None]:
    r"""Retrieve pages of all the categories that Fractal currently supports.

    Category id and the category name are returned in the response.

    :param client: Live or Sandbox API Client
    :type client: ApiClient
    :yield: A generator of pages of categories
    :rtype: Generator[List[Category], None, None]
    """
    yield from _get_paged_response(
        client=client, url=categories, cls=Category, param_keys=None, company_id=None
    )
