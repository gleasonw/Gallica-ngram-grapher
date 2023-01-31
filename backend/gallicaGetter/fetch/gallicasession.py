import time
from typing import Any
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import requests
from requests.exceptions import RetryError
from dataclasses import dataclass


@dataclass(slots=True)
class Response:
    xml: bytes
    query: Any
    elapsed: float


class GallicaSession:
    def __init__(self, maxSize):
        self.maxSize = maxSize
        self.session = self.build_session()
    # don't retry on 503, need to catch
    def build_session(self):
        retry_strategy = Retry(
            total=10,
            status_forcelist=[429, 500, 502, 504],
            backoff_factor=1,
            connect=20,
            read=20,
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_maxsize=self.maxSize,
            pool_connections=self.maxSize,
        )
        session = requests.Session()
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def get(self, query) -> Response:
        start = time.perf_counter()
        try:
            response = self.session.get(
                query.endpoint_url, params=query.get_params_for_fetch()
            )
        except RetryError:
            print("retry error")
            return Response(b"", query, 0)
        end = time.perf_counter()
        if response.status_code != 200:
            print(f"Gallica HTTP response Error: {response.status_code}")
            return Response(b"", query, 0)
        return Response(xml=response.content, query=query, elapsed=end - start)
