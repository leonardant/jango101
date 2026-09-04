from api.models import APIClientCredential


def regenerate_client_secret(
    credential: APIClientCredential,
) -> str:
    """
    Generate and store a new client secret.

    The raw secret is returned so it can be displayed once to
    the administrator. Only the hashed version is stored.
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