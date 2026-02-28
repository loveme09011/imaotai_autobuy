import pytest
import requests

from api.client import ApiClient, BASE_URL


@pytest.fixture
def client():
    return ApiClient({
        "token": "Bearer test_token",
        "device_id": "test_device",
        "user_id": "test_user",
    })


@pytest.fixture
def mock_response(mocker):
    resp = mocker.Mock()
    resp.status_code = 200
    resp.raise_for_status = mocker.Mock()
    return resp


class TestApiClientHeaders:
    def test_get_headers_contains_required_fields(self, client):
        headers = client._get_headers("/test", "1700000000000")
        assert headers["MT-Device-ID"] == "test_device"
        assert headers["MT-APP-Version"] == "1.7.6"
        assert headers["Authorization"] == "Bearer test_token"
        assert "mt-k" in headers
        assert "mt-r" in headers

    def test_mt_k_includes_user_id(self, client, mocker):
        mock_sign = mocker.patch("api.client.generate_sign", return_value="abc123")
        client._get_headers("/test", "1700000000000")
        calls = mock_sign.call_args_list
        # mt-k call includes user_id
        assert calls[0] == mocker.call("/test", "1700000000000", "test_device", "test_user")
        # mt-r call excludes user_id
        assert calls[1] == mocker.call("/test", "1700000000000", "test_device")


class TestApiClientRequest:
    def test_successful_request(self, client, mocker, mock_response):
        mock_response.json.return_value = {"code": 200}
        mocker.patch.object(client.session, "request", return_value=mock_response)
        result = client._request("GET", "/test")
        assert result == {"code": 200}

    def test_retries_on_failure(self, client, mocker, mock_response):
        mock_response.json.return_value = {"code": 200}
        mocker.patch("api.client.time.sleep")
        mocker.patch.object(
            client.session,
            "request",
            side_effect=[
                requests.ConnectionError("fail"),
                mock_response,
            ],
        )
        result = client._request("GET", "/test")
        assert result == {"code": 200}
        assert client.session.request.call_count == 2

    def test_raises_after_max_retries(self, client, mocker):
        mocker.patch("api.client.time.sleep")
        mocker.patch.object(
            client.session,
            "request",
            side_effect=requests.ConnectionError("fail"),
        )
        with pytest.raises(requests.ConnectionError):
            client._request("GET", "/test")
        assert client.session.request.call_count == 3


class TestSendCode:
    def test_send_code(self, client, mocker, mock_response):
        mock_response.json.return_value = {"code": 200}
        mocker.patch.object(client.session, "request", return_value=mock_response)
        result = client.send_code("13800138000")
        assert result == {"code": 200}
        call_args = client.session.request.call_args
        assert call_args[0][0] == "POST"
        assert "/sendCode" in call_args[0][1]


class TestLogin:
    def test_login_returns_token_and_user_id(self, client, mocker, mock_response):
        mock_response.json.return_value = {"token": "new_token", "userId": "12345"}
        mocker.patch.object(client.session, "request", return_value=mock_response)
        result = client.login("13800138000", "1234", "dev_id")
        assert result == {"token": "new_token", "user_id": "12345"}


class TestGetItems:
    def test_get_items_returns_list(self, client, mocker, mock_response):
        mock_response.json.return_value = {"data": [{"id": "1"}, {"id": "2"}]}
        mocker.patch.object(client.session, "request", return_value=mock_response)
        result = client.get_items()
        assert result == [{"id": "1"}, {"id": "2"}]


class TestGetShops:
    def test_get_shops_returns_list(self, client, mocker, mock_response):
        mock_response.json.return_value = {"data": [{"shopId": "s1"}]}
        mocker.patch.object(client.session, "request", return_value=mock_response)
        result = client.get_shops("110000")
        assert result == [{"shopId": "s1"}]


class TestReservation:
    def test_reservation(self, client, mocker, mock_response):
        mock_response.json.return_value = {"code": 200, "message": "success"}
        mocker.patch.object(client.session, "request", return_value=mock_response)
        result = client.reservation("item1", "shop1")
        assert result["code"] == 200


class TestTravel:
    def test_travel(self, client, mocker, mock_response):
        mock_response.json.return_value = {"code": 200, "travelReward": 100}
        mocker.patch.object(client.session, "request", return_value=mock_response)
        result = client.travel()
        assert result["code"] == 200
