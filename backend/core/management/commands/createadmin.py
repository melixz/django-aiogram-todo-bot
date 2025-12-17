from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create a superuser with default credentials (admin/admin)"

    def handle(self, *args, **options):
        User = get_user_model()
        username = "admin"
        email = "admin@example.com"
        password = "admin"

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f"User '{username}' already exists. Skipping creation.")
            )
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(
            self.style.SUCCESS(
                f"Superuser '{username}' created successfully!\n"
                f"Username: {username}\n"
                f"Password: {password}\n"
                f"Login at: http://localhost:8000/admin/"
            )
        )



