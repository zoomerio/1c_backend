
import httpx
from typing import Dict, Optional
from loguru import logger

class RequestHelper:
    def __init__(self, headers: Optional[Dict[str, str]] = None, logging: bool = True):
        self.headers = headers or {}
        self.session = httpx.AsyncClient(headers=self.headers)
        if not logging:
            logger.disable(__name__)

    async def request(self, method, url, **kwargs):
        logger.debug(f"Request {method} {url}")
        try:
            response = await self.session.request(method, url, **kwargs)
        except httpx.ConnectError as e:
            logger.error(f"Error occured: {e}")
            return {}

        logger.debug(f"Response content type: {response.headers.get('Content-Type')}, response status: {response.status_code}, done in {response.elapsed.total_seconds()}")
        return response

    async def get(self, url, **kwargs):
        return await self.request("GET", url, **kwargs)

    async def post(self, url, **kwargs):
        return await self.request("POST", url, **kwargs)

    async def put(self, url, **kwargs):
        return await self.request("PUT", url, **kwargs)

    async def delete(self, url, **kwargs):
        return await self.request("DELETE", url, **kwargs)

    async def update(self, url, **kwargs):
        return await self.request("PATCH", url, **kwargs)

    async def options(self, url, **kwargs):
        return await self.request("OPTIONS", url, **kwargs)

