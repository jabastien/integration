"""Class for themes in HACS."""
from custom_components.hacs.helpers.classes.exceptions import HacsException
from custom_components.hacs.helpers.functions.information import find_file_name
from custom_components.hacs.helpers.functions.logger import getLogger

from custom_components.hacs.helpers.classes.repository import HacsRepository


class HacsTheme(HacsRepository):
    """Themes in HACS."""

    def __init__(self, full_name):
        """Initialize."""
        super().__init__()
        self.data.full_name = full_name
        self.data.category = "theme"
        self.content.path.remote = "themes"
        self.content.path.local = self.localpath
        self.content.single = False
        self.logger = getLogger(f"repository.{self.data.category}.{full_name}")

    @property
    def localpath(self):
        """Return localpath."""
        return f"{self.hacs.system.config_path}/themes/{self.data.file_name.replace('.yaml', '')}"

    async def async_post_installation(self):
        """Run post installation steps."""
        try:
            await self.hacs.hass.services.async_call("frontend", "reload_themes", {})
            self.logger.info("Themes reloaded")
        except (Exception, BaseException):  # pylint: disable=broad-except
            pass

    async def validate_repository(self):
        """Validate."""
        # Run common validation steps.
        await self.common_validate()

        # Custom step 1: Validate content.
        compliant = False
        for treefile in self.treefiles:
            if treefile.startswith("themes/") and treefile.endswith(".yaml"):
                compliant = True
                break
        if not compliant:
            raise HacsException(
                f"Repostitory structure for {self.ref.replace('tags/','')} is not compliant"
            )

        if self.data.content_in_root:
            self.content.path.remote = ""

        # Handle potential errors
        if self.validate.errors:
            for error in self.validate.errors:
                if not self.hacs.system.status.startup:
                    self.logger.error(error)
        return self.validate.success

    async def async_post_registration(self):
        """Registration."""
        # Set name
        find_file_name(self)
        self.content.path.local = self.localpath

    async def update_repository(self, ignore_issues=False):
        """Update."""
        await self.common_update(ignore_issues)

        # Get theme objects.
        if self.data.content_in_root:
            self.content.path.remote = ""

        # Update name
        find_file_name(self)
        self.content.path.local = self.localpath
