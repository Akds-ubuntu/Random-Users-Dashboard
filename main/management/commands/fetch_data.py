from django.core.management.base import BaseCommand
from main.services import RandomUserService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Кастомная команда управления для
    первоначальной загрузки пользователей.
    """
    help = "Load initial users from external API"

    def handle(self, *args, **options):
        from main.models import RandomUser

        if RandomUser.objects.exists():
            self.stdout.write(
                self.style.SUCCESS(
                    "Users already loaded, skipping initial load."
                )
            )
            return
        service = RandomUserService()
        try:
            self.stdout.write(
                "Starting initial user load from API..."
            )
            service.load_initial_users(1000)
            self.stdout.write(self.style.SUCCESS(
                "Initial user load completed successfully.")
            )
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"Failed to load initial users: {e}")
            )
            logger.error(
                f"Failed to load initial users: {e}"
            )
            raise
