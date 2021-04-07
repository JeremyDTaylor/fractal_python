# -*- coding: utf-8 -*-
import json

import arrow
import pytest

from fractal_python import api_client
from fractal_python.api_client import ApiClient

TOKEN_RESPONSE = {
    "access_token": "access token e.g. knkjkd123ldk",
    "partner_id": "Partner ID e.g. 1juji12f",
    "expires_in": 1800,
    "token_type": "Bearer",
}


def make_sandbox(requests_mock) -> ApiClient:
    requests_mock.register_uri("POST", "/token", text=json.dumps(TOKEN_RESPONSE))
    return api_client.sandbox("sandbox-key", "sandbox-partner")


@pytest.fixture()
def sandbox(requests_mock) -> ApiClient:
    return make_sandbox(requests_mock)


@pytest.fixture
def live(requests_mock) -> ApiClient:
    requests_mock.register_uri("POST", "/token", text=json.dumps(TOKEN_RESPONSE))
    return api_client.live("live-key", "live-partner")


def test_sandbox(sandbox):
    assert "sandbox-key" in sandbox.headers.values()
    assert "sandbox-partner" in sandbox.headers.values()


def test_live(live):
    assert "live-key" in live.headers.values()
    assert "live-partner" in live.headers.values()


def test_authorise(requests_mock, freezer, sandbox):
    requests_mock.register_uri("POST", "/token", text=json.dumps(TOKEN_RESPONSE))
    sandbox.expires_at = arrow.now().shift(seconds=-1801)
    sandbox.authorise()
    assert (
        sandbox.expires_at.int_timestamp
        == arrow.now().shift(seconds=1800).int_timestamp
    )
