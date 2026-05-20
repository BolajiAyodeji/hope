import os

from hope.apps.core.api.mixins import BaseAPI


class VisionAPI(BaseAPI):
    API_KEY_ENV_NAME = "VISION_API_KEY"
    API_URL_ENV_NAME = "VISION_API_URL"
    API_COOKIE_ENV_NAME = "VISION_API_COOKIE"

    class VisionAPIError(Exception):
        pass

    class VisionAPIMissingCredentialsError(Exception):
        pass

    API_EXCEPTION_CLASS = VisionAPIError  # type: ignore[assignment]
    API_MISSING_CREDENTIALS_EXCEPTION_CLASS = VisionAPIMissingCredentialsError  # type: ignore[assignment]

    def __init__(self) -> None:
        super().__init__()
        self._client.headers["Authorization"] = f"Bearer {self.api_key}"
        cookie = os.getenv(self.API_COOKIE_ENV_NAME)
        if cookie:
            self._client.headers["Cookie"] = cookie

    class Endpoints:
        PP_INBOUND = "http/hope/pp/inbound"

    def _post_to(self, endpoint: str, data: dict) -> dict:
        return self._post(self.get_url(endpoint), data)[0]

    def _get_from(self, endpoint: str, params: dict | None = None) -> dict:
        return self._get(self.get_url(endpoint), params)[0]

    def send_payment_plan(self, data: dict) -> dict:
        return self._post_to(self.Endpoints.PP_INBOUND, data)
