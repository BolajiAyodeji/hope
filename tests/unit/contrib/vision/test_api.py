import os
from unittest.mock import patch

import pytest

from hope.contrib.vision.api import VisionAPI


@pytest.fixture(autouse=True)
def mock_vision_env_vars() -> None:
    with patch.dict(
        os.environ,
        {
            "VISION_API_KEY": "test-token",
            "VISION_API_URL": "https://test.example.com/",
            "VISION_API_COOKIE": "sap-session=abc123; sap-client=350",
        },
    ):
        yield


class TestInit:
    def test_missing_credentials_raises_error(self) -> None:
        with patch.dict(
            os.environ,
            {"VISION_API_KEY": "", "VISION_API_URL": ""},
            clear=True,
        ):
            with pytest.raises(VisionAPI.VisionAPIMissingCredentialsError):
                VisionAPI()

    def test_sets_bearer_auth(self) -> None:
        api = VisionAPI()
        assert api._client.headers["Authorization"] == "Bearer test-token"

    def test_sets_cookie_when_env_var_present(self) -> None:
        api = VisionAPI()
        assert api._client.headers.get("Cookie") == "sap-session=abc123; sap-client=350"

    def test_no_cookie_when_env_var_missing(self) -> None:
        with patch.dict(
            os.environ,
            {"VISION_API_KEY": "k", "VISION_API_URL": "u", "VISION_API_COOKIE": ""},
        ):
            api = VisionAPI()
            assert "Cookie" not in api._client.headers


class TestPaymentPlan:
    @patch("hope.contrib.vision.api.VisionAPI._post")
    def test_send_payment_plan(self, mock_post) -> None:
        mock_post.return_value = ({"status": "ok"}, 200)
        api = VisionAPI()
        result = api.send_payment_plan({"messageId": "Plan-001"})
        assert result == {"status": "ok"}
        mock_post.assert_called_once_with(
            "https://test.example.com/http/hope/pp/inbound",
            {"messageId": "Plan-001"},
        )


class TestHelpers:
    @patch("hope.contrib.vision.api.VisionAPI._post")
    def test_post_to(self, mock_post) -> None:
        mock_post.return_value = ({"result": "created"}, 201)
        api = VisionAPI()
        result = api._post_to("http/hope/pp/inbound", {"key": "val"})
        assert result == {"result": "created"}
        mock_post.assert_called_once_with(
            "https://test.example.com/http/hope/pp/inbound",
            {"key": "val"},
        )

    @patch("hope.contrib.vision.api.VisionAPI._get")
    def test_get_from(self, mock_get) -> None:
        mock_get.return_value = ({"data": []}, 200)
        api = VisionAPI()
        result = api._get_from("http/hope/pp/status", {"param": "x"})
        assert result == {"data": []}
        mock_get.assert_called_once_with(
            "https://test.example.com/http/hope/pp/status",
            {"param": "x"},
        )


class TestCustomExceptions:
    def test_vision_api_error_is_raised(self) -> None:
        with patch.dict(
            os.environ,
            {"VISION_API_KEY": "k", "VISION_API_URL": "u"},
        ):
            with patch("hope.contrib.vision.api.VisionAPI._post") as mock_post:
                mock_post.side_effect = VisionAPI.VisionAPIError("boom")
                api = VisionAPI()
                with pytest.raises(VisionAPI.VisionAPIError):
                    api._post_to("/endpoint", {})
