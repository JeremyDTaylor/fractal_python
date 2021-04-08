# -*- coding: utf-8 -*-
from typing import Generator, List

import attr
import deserialize  # type: ignore

from fractal_python.api_client import ApiClient, _get_paged_response
from fractal_python.banking.api import BANKING_ENDPOINT

merchants = BANKING_ENDPOINT + "/merchants"


@attr.s(auto_attribs=True)
@deserialize.auto_snake()
class Merchant:
    id: str
    name: str
    category_code: str
    address_line: str


def retrieve_merchants(client: ApiClient) -> Generator[List[Merchant], None, None]:
    r"""Retrieves pages of all the merchants that are currently categorised by Fractal.
    Merchant id and the merchant name are returned in the response.

    :param client: Live or Sandbox API Client
    :type client: ApiClient
    :yield: Pages of Merchants
    :rtype: Generator[List[Merchant], None, None]
    """
    yield from _get_paged_response(
        client=client,
        company_id=None,
        params=None,
        url=merchants,
        cls=Merchant,
    )
