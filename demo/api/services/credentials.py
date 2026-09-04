from ..models import APIClientCredential


def regenerate_client_secret(
    credential: APIClientCredential,
) -> str:
    """
    Generate a new client secret, store only its hashed version,
    and return the raw secret.

    The raw secret should only be displayed once.
    """

    raw_secret = (
        APIClientCredential.generate_client_secret()
    )

    credential.set_client_secret(
        raw_secret
    )

    credential.save(
        update_fields=[
            "client_secret",
            "updated_at",
        ]
    )

    return raw_secret