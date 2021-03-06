from custom_components.hacs.helpers.functions.logger import getLogger
from custom_components.hacs.share import get_hacs


class ValidationException(Exception):
    pass


class ValidationBase:
    def __init__(self, repository) -> None:
        self.repository = repository
        self.hacs = get_hacs()
        self.failed = False
        self.logger = getLogger(f"{repository.data.category}.check")

    @property
    def action_only(self):
        return False

    async def _async_run_check(self):
        """DO NOT OVERRIDE THIS IN SUBCLASSES!"""
        if self.hacs.action:
            self.logger.info(f"Running check '{self.__class__.__name__}'")
        try:
            await self.hacs.hass.async_add_executor_job(self.check)
            await self.async_check()
        except ValidationException as exception:
            self.failed = True
            self.logger.error(exception)

    def check(self):
        pass

    async def async_check(self):
        pass


class ActionValidationBase(ValidationBase):
    @property
    def action_only(self):
        return True
