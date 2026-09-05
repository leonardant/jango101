from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

from api.models import APIClientCredential


User = get_user_model()


class Command(BaseCommand):
    help = "Create API credentials for a user"

    def add_arguments(self, parser):

        parser.add_argument(
            "username",
            type=str,
            help="Username of the user",
        )

    def handle(self, *args, **options):

        username = options["username"]

        try:
            user = User.objects.get(username=username)

        except User.DoesNotExist:
            raise CommandError(f'User "{username}" does not exist.')

        # Check whether credentials already exist
        if APIClientCredential.objects.filter(user=user).exists():
            self.stdout.write(
                self.style.WARNING(f"API credentials already exist for {username}.")
            )

            self.stdout.write(
                self.style.WARNING(
                    "Create new credentials only after rotating or deleting "
                    "the existing credentials."
                )
            )

            return

        # Generate credentials
        client_id = APIClientCredential.generate_client_id()

        raw_client_secret = APIClientCredential.generate_client_secret()

        # Create credential record
        credential = APIClientCredential(
            user=user,
            client_id=client_id,
        )

        # Hash and store the secret
        credential.set_client_secret(raw_client_secret)

        credential.save()

        # Display credentials
        self.stdout.write(self.style.SUCCESS(f"API credentials created for {username}"))

        self.stdout.write(f"Client ID: {client_id}")

        self.stdout.write(self.style.WARNING(f"Client Secret: {raw_client_secret}"))

        self.stdout.write(
            self.style.WARNING(
                "IMPORTANT: Save the client secret now. It cannot be recovered later."
            )
        )
