import os
from os import sys, path
import logging
from logging import Logger
from injector import provider, singleton, Module
from pyfortified_logging import get_logger, LoggingFormat, LoggingOutput
from consul_client import ConsulClient
from postgres_client import PostgresClient
from config_service import ConfigService
from async_virus_total_client import VirusTotalClient


sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))


class CoreModule(Module):
    """config modules"""
    @singleton
    @provider
    def provide_consul_client(self) -> ConsulClient:
        """innit consul client"""
        consul_client = ConsulClient(host=os.getenv('CONSUL_HOST', '127.0.0.1'), prefix='sites-checker-service')
        return consul_client

    @singleton
    @provider
    def provide_postgres_client(self, conf_service: ConfigService) -> PostgresClient:
        """init Postgres client"""
        postgres_client = PostgresClient(dsn=conf_service.postgres_url)
        # TODO: check asyncio support
        # await postgres_client.connect()
        return postgres_client

    @singleton
    @provider
    def provide_virus_total_client(self, conf_service: ConfigService) -> VirusTotalClient:
        """init virus_total_client client"""
        virus_total_client = VirusTotalClient(apikey=conf_service.vt_apikey)
        # TODO: check asyncio support
        return virus_total_client

    @singleton
    @provider
    def provide_logger(self) -> Logger:
        """innit logger"""
        logger = get_logger(
            logger_name='SitesCheckerService',
            logger_format=LoggingFormat.JSON,
            logger_level=logging.INFO,
            logger_output=LoggingOutput.STDOUT,
        )
        return logger
