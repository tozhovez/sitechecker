#key='6bc85c06f769fe6e606eaa4e47648723bbc5f3e42bb627dc327b867b5c7f014c'
import os
import asyncio
import logging
from os import sys, path

_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'core'))

sys.path.append(_dir)

from core.async_virus_total_client import VirusTotalClient, APIError


class VT:
    def __init__(self, apikey):
        self.vt_client = None
        self.apikey = apikey

    async def type_base_url(self, site_name, base_url_type='domains'):
        vt_base_url = {
            'domains':'https://www.virustotal.com/api/v3/domains',
            'ip':'https://www.virustotal.com/api/v3/ip_addresses',
            'url': 'https://www.virustotal.com/api/v3/urls',
        }
        return f'{vt_base_url[base_url_type]}/{site_name}'


    async def get_data(self, request, base_url_type='domains'):
        base_url = await self.type_base_url(request, base_url_type)
        async with VirusTotalClient(apikey=self.apikey) as vt_client:
            try:
                result = await vt_client.fetch(url=base_url)
                if not result or (result and 'data' not in result):
                    raise ValueError('Object {} not found'.format(request))
                return result['data']
            except APIError as ex:
                raise ex
