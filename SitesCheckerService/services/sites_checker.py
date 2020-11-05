import os
import os.path
import asyncio
from datetime import datetime
from logging import Logger
from injector import singleton, inject

from core.postgres_client import PostgresClient
from core.config_service import ConfigService
from core.async_virus_total_client import VirusTotalClient


@singleton
class SitesChecker:
    """SitesCheckerService"""
    @inject
    def __init__(self):
        pass

    async def start_run(self):
        print(f"wooork getting URL: ")

    async def close(self):
        print(f"wooork elapsed time: ")






#
#
# async def task(name, work_queue):
#     async with aiohttp.ClientSession() as session:
#         while not work_queue.empty():
#             url = await work_queue.get()
#             print(f"Task {name} getting URL: {url}")
#             et = ET()
#             async with session.get(url) as response:
#                 await response.text()
#             print(f"Task {name} total elapsed time: {et():.1f}")
#
# async def main():
#     """
#     This is the main entry point for the program.
#     """
#     # Create the queue of 'work'
#     work_queue = asyncio.Queue()
#
#     # Put some 'work' in the queue
#     for url in [
#         "http://google.com",
#         "http://yahoo.com",
#         "http://linkedin.com",
#         "http://apple.com",
#         "http://microsoft.com",
#         "http://facebook.com",
#         "http://twitter.com",
#     ]:
#         await work_queue.put(url)
#
#     # Run the tasks
#     et = ET()
#     await asyncio.gather(
#         asyncio.create_task(task("One", work_queue)),
#         asyncio.create_task(task("Two", work_queue)),
#     )
#     print(f"\nTotal elapsed time: {et():.1f}")
#
# if __name__ == "__main__":
#     asyncio.run(main())
