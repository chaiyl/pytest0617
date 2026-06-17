from collections.abc import Mapping
from typing import Any

import requests


class HttpClient:
    def __init__(
        self,
        base_url: str,
        timeout: int = 10,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        if headers:
            self.session.headers.update(headers)

    def request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        kwargs.setdefault("timeout", self.timeout)
        return self.session.request(method=method.upper(), url=self._url(path), **kwargs)

    def get(
        self,
        path: str,
        params: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        return self.request("GET", path, params=params, **kwargs)

    def post(
        self,
        path: str,
        json: Any | None = None,
        data: Any | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        return self.request("POST", path, json=json, data=data, **kwargs)

    def put(
        self,
        path: str,
        json: Any | None = None,
        data: Any | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        return self.request("PUT", path, json=json, data=data, **kwargs)

    def patch(
        self,
        path: str,
        json: Any | None = None,
        data: Any | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        return self.request("PATCH", path, json=json, data=data, **kwargs)

    def delete(
        self,
        path: str,
        json: Any | None = None,
        data: Any | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        return self.request("DELETE", path, json=json, data=data, **kwargs)

    def upload(
        self,
        path: str,
        files: Mapping[str, Any],
        data: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        return self.request("POST", path, files=files, data=data, **kwargs)

    def set_headers(self, headers: Mapping[str, str]) -> None:
        self.session.headers.update(headers)

    def set_bearer_token(self, token: str) -> None:
        self.set_headers({"Authorization": f"Bearer {token}"})

    def remove_header(self, name: str) -> None:
        self.session.headers.pop(name, None)

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()

    def _url(self, path: str) -> str:
        if path.startswith(("http://", "https://")):
            return path
        return f"{self.base_url}/{path.lstrip('/')}"
