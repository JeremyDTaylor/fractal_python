import json
from urllib.parse import quote

import arrow
import requests

SANDBOX = "https://sandbox.askfractal.com"
LIVE = "https://api.askfractal.com"
API_KEY_HEADER = "X-Api-Key"
PARTNER_ID_HEADER = "X-Partner-Id"


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
        path_params=None,
        query_params=None,
        body=None,
    ) -> requests.Response:
        if path_params:
            for k, v in path_params.items():
                resource_path = resource_path.replace("%s" % k, quote(str(v)))
        url = self.base_url + resource_path
        self.authorise()
        return requests.request(
            method, url, params=query_params, headers=self.headers, data=body
        )

    def authorise(self):
        now = arrow.now()
        if now > self.expires_at:
            url = self.base_url + "/token"
            self.headers.pop("Authorization", None)
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
