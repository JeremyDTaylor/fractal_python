import json
from typing import Any, Optional

import arrow
import requests

SANDBOX = "https://sandbox.askfractal.com"
LIVE = "https://api.askfractal.com"
API_KEY_HEADER = "X-Api-Key"
PARTNER_ID_HEADER = "X-Partner-Id"
COMPANY_ID_HEADER = "X-Company-Id"
AUTHORIZATION_HEADER = "Authorization"


class ApiClient(object):
    def __init__(self, base_url: str, api_key: str, partner_id: str):
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
        query_params: dict[str, Any] = None,
        body: str = None,
        call_headers: dict = None,
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
        query_params: Optional[dict[str, str]] = None,
        body: Optional[str] = None,
        call_headers: Optional[dict[str, str]] = None,
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
    return ApiClient(SANDBOX, api_key, partner_id)


def live(api_key: str, partner_id: str) -> ApiClient:
    return ApiClient(LIVE, api_key, partner_id)
