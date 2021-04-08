# -*- coding: utf-8 -*-
import json
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Collection, Dict, Generator, List, Optional, Type

import arrow
import deserialize
import requests
from stringcase import camelcase

SANDBOX = "https://sandbox.askfractal.com"
LIVE = "https://api.askfractal.com"
API_KEY_HEADER = "X-Api-Key"
PARTNER_ID_HEADER = "X-Partner-Id"
COMPANY_ID_HEADER = "X-Company-Id"
AUTHORIZATION_HEADER = "Authorization"


class ApiClient:
    def __init__(self, base_url: str, api_key: str, partner_id: str):
        r"""Fractal API Client.

        :param base_url: url for the API
        :param api_key: Secret API Key
        :param partner_id: Unique partner id
        """
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            API_KEY_HEADER: api_key,
            PARTNER_ID_HEADER: partner_id,
        }
        self.expires_at = arrow.now()

    def call_api(
        self,
        resource_path: str,
        method: str,
        query_params: Dict[str, Any] = None,
        body: Optional[str] = None,
        call_headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        url = self.base_url + resource_path
        return self.call_url(
            url=url,
            method=method,
            query_params=query_params,
            body=body,
            call_headers=call_headers,
        )

    def call_url(
        self,
        url: str,
        method: str,
        query_params: Optional[Dict[str, Any]] = None,
        body: Optional[str] = None,
        call_headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        self.authorise()
        call_headers = call_headers or {}
        call_headers.update(self.headers)
        return requests.request(
            method, url, params=query_params, headers=call_headers, data=body
        )

    def authorise(self):
        now = arrow.now()
        if now > self.expires_at:
            url = self.base_url + "/token"
            self.headers.pop(AUTHORIZATION_HEADER, None)
            response = requests.request("POST", url, headers=self.headers)
            json_response = json.loads(response.text)
            self.expires_at = now.shift(seconds=int(json_response["expires_in"]))
            token_type = json_response["token_type"]
            access_token = json_response["access_token"]
            self.headers["Authorization"] = f"{token_type} {access_token}"


def sandbox(api_key: str, partner_id: str) -> ApiClient:
    r"""
    Returns a client for the sandbox api.

    :param api_key: secret key issued to the partner
    :param partner_id: unique if of the partner
    :return: an ApiClient for the sandbox
    :rtype: ApiClient

    Usage::

      >>> from fractal_python import api_client
      >>> client = api_client.sandbox('secret key', 'partner id')
    """
    return ApiClient(SANDBOX, api_key, partner_id)


def live(api_key: str, partner_id: str) -> ApiClient:
    r"""
    Returns a client for the live api.

    :param api_key: secret key issued to the partner
    :param partner_id: unique if of the partner
    :return: an ApiClient for the live system
    :rtype: ApiClient

    Usage::

      >>> from fractal_python import api_client
      >>> client = api_client.sandbox('secret key', 'partner id')
    """
    return ApiClient(LIVE, api_key, partner_id)


def _call_api(
    client: ApiClient,
    url: str,
    method: str,
    query_params: Dict[str, Any] = None,
    body: str = None,
    company_id: str = None,
) -> requests.Response:
    headers = {COMPANY_ID_HEADER: company_id} if company_id else {}
    response: requests.Response = client.call_api(
        url, method, query_params=query_params, body=body, call_headers=headers
    )
    return response


def _handle_get_response(response, cls):
    json_response = json.loads(response.text)
    results = deserialize.deserialize(List[cls], json_response.get("results", None))
    next_page = json_response.get("links", {}).get("next", None)
    return results, next_page


def _get_paged_response(
    client: ApiClient,
    company_id: Optional[str],
    params: Optional[Collection[str]],
    url: str,
    cls: Type,
    **kwargs,
) -> Generator:
    query_params = (
        {camelcase(key): kwargs[key] for key in params if key in kwargs}
        if params
        else {}
    )
    response = _call_api(
        client=client,
        url=url,
        method="GET",
        query_params=query_params,
        company_id=company_id,
    )
    headers = {COMPANY_ID_HEADER: company_id} if company_id else {}
    results, next_page = _handle_get_response(response, cls)
    yield results
    while next_page:
        response = client.call_url(next_page, "GET", call_headers=headers)
        results, next_page = _handle_get_response(response, cls)
        yield results


def _arrow_or_none(value: Any):
    return arrow.get(value) if value else None


def _money_amount(value: Any):
    return Decimal(value).quantize(Decimal("0.01"), ROUND_HALF_UP) if value else None
