from os import sys, path
import asyncio
from logging import Logger
from datetime import datetime
from injector import singleton, inject
from jobs.job_manager import JobManager
from core.consul_client import ConsulClient
from core.postgres_client import PostgresClient
from core.config_service import ConfigService

from services.sites_checker import SitesChecker
from status_code import StatusCode

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))


@singleton
class SitesCheckerService:
    @inject
    def __init__(self,
                 logger: Logger,
                 jobs_manager: JobManager,
                 cnsl_client: ConsulClient,
                 pg_client: PostgresClient,
                 config_service: ConfigService,
                 sites_checker: SitesChecker
    ):
        self.logger = logger
        self.job_manager = jobs_manager
        self.consul_client = cnsl_client
        self.postgres_client = pg_client
        self.config_service = config_service
        self.sites_checker = sites_checker
        self.service_start_time = None

    async def status(self):
        status_code = 0

        service_state = {
            'status_code': 0,
        }

        return {
            'status_code': 0,
        }

    async def kill(self):
        """Graceful exit"""
        if self.job_manager:
            await self.job_manager.close()
        #if self.postgres_client:
        #   self.postgres_client.close()
        #if self.virus_total_client:
        #   await self.virus_total_client.close()
        #if self.sites_checker:
        #   await self.sites_checker.close()

    async def _up_check(self):
        try:
            self.logger.info(f'SitesCheckerService start up {self.service_start_time}')
            await self.sites_checker.start_run()

        except Exception as ex:
            self.logger.error('Unexpected error was raised while trying to log service state', exc_info=True)
            await self.kill()
        finally:
            self.logger.info(f'SitesCheckerService down')

    async def run(self):

        self.service_start_time = datetime.utcnow()

        try:
            self.consul_client.connect()
            #self.postgres_client.connect()
            #self.virus_total_client.connect()
        except Exception as ex:
            self.logger.info('Cannot connect to infra services', exc_info=True)
            exit(1)

        # start background jobs
        self.job_manager.start()

        #self.job_manager.add_interval_job(self._up_check, 5)
        await self.job_manager.run_once(self._up_check)

        self.logger.info(f'SitesCheckerService has started {self.service_start_time}')
