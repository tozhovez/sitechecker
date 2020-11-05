from sanic import Blueprint
from sanic.response import json
from injector import inject, singleton
from logging import Logger
from sites_checker_service import SitesCheckerService


@singleton
class HealthCheckController:
    @inject
    def __init__(self, logger: Logger, sites_checker_service: SitesCheckerService):
        self.logger = logger
        self.sites_checker_service = sites_checker_service

    async def check_health(self, request):
        # get current state
        service_state = await self.sites_checker_service.status()

        # write response
        response_message = "SitesChecker Service is healthy."
        res_status = 200
        if service_state['status_code'] != 0:
            response_message = f"SitesChecker Service isn't healthy"
            res_status = 500
            self.logger.error("SitesChecker Service isn't healthy.", extra=service_state)

        return json({"message": response_message, "serviceState": service_state}, status=res_status)


# ! TEMPORARY
def create_health_check_controller(health_check_controller: HealthCheckController, app):
    health_check_bp = Blueprint('health_check')

    @health_check_bp.route('/health_check')
    async def decorated_get_health_check(request):
        return await health_check_controller.check_health(request)

    app.blueprint(health_check_bp)
