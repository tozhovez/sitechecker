from os import sys, path
import asyncio
import aiohttp
from logging import Logger

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))


class APIError(Exception):
    """Class that encapsules errors returned by the VirusTotal API."""
    @classmethod
    def from_dict(cls, dict_error):
        """errors returned by the VirusTotal API from dict"""
        return cls(dict_error['code'], dict_error.get('message'))

    def __init__(self, code, message):
        self.code = code
        self.message = message
        self.print_error()


    def print_error(self):
        return str(f"{self.code} {self.message}")


class VirusTotalClient:
    """Client for interacting with VirusTotal."""

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self._session = None


    async def __aenter__(self):
        """connect """
        kw = self.kwargs
        if not self._session:
            self._session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=False),
                headers={
                    'X-Apikey': kw.get('apikey'),
                    'Accept': 'application/json',
                    }
                )
        return self



    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_async()



    async def close_async(self):
        """close returns a coroutine."""

        if self._session:
            await self._session.close()
            self._session = None


    async def fetch(self, url):
        async with self._session.get(url) as response:
            if response.status == 200:
                json_response = await response.json()
                return json_response
            if response.status in (503, 429):
                await asyncio.sleep(45.5)

                raise APIError('RetryLater', await response.text())
            if response.status >= 400 and response.status <= 499:
                if response.content_type == 'application/json':
                    json_response = await response.json()
                    error = json_response.get('error')
                    if error:
                        raise APIError.from_dict(error)
                raise APIError('ClientError',  await response.text())
            raise APIError('ServerError',  await response.text())
