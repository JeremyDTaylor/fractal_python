from urllib.parse import quote
import requests

SANDBOX = "https://sandbox.askfractal.com"
LIVE = "https://api.askfractal.com"
API_KEY_HEADER = "X-Api-Key"
PARTNER_ID_HEADER = "X-Partner-Id"


class ApiClient(object):
    def __init__(self, base_url: str, api_key: str, partner_id: str):
        self.base_url = base_url
        self.default_headers = {
            "Content-Type": "application/json",
            API_KEY_HEADER: api_key,
            PARTNER_ID_HEADER: partner_id,
        }

    def call_api(
        self,
        resource_path: str,
        method: str,
        path_params=None,
        query_params=None,
        body=None,
    ) -> requests.request:
        if path_params:
            for k, v in path_params:
                resource_path = resource_path.replace("{%s}" % k, quote(str(v)))
        url = self.base_url + resource_path
        return requests.request(
            method, url, params=query_params, headers=self.default_headers, data=body
        )

    def get_token(self) -> requests.request:
        return self.call_api("/token", "POST")


def sandbox(api_key: str, partner_id: str) -> ApiClient:
    return ApiClient(SANDBOX, api_key, partner_id)


def live(api_key: str, partner_id: str) -> ApiClient:
    return ApiClient(LIVE, api_key, partner_id)
