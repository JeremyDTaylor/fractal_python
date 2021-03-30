from fractal_python import api_client


def test_sandbox():
    client = api_client.sandbox("sandbox-key", "sandbox-partner")
    assert "sandbox-key" in client.default_headers.values()
    assert "sandbox-partner" in client.default_headers.values()


def test_live():
    client = api_client.live("live-key", "live-partner")
    assert "live-key" in client.default_headers.values()
    assert "live-partner" in client.default_headers.values()


def test_get_token(requests_mock):
    client = api_client.ApiClient("http://123-fake-api.com", "key", "id")
    requests_mock.register_uri(
        "POST", "http://123-fake-api.com/token", text="test_get_token"
    )
    response = client.get_token()
    assert response.text == "test_get_token"
