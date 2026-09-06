import os

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

import pytest
from django.conf import settings
from django.urls import reverse


@pytest.fixture
def authenticated_page(
    page,
    live_server,
    django_user_model,
):
    settings.API_BASE_URL = live_server.url + "/api/"

    username = "playwright_user"
    password = "TestPassword123!"

    django_user_model.objects.create_user(
        username=username,
        password=password,
    )

    login_url = live_server.url + reverse(
        "login",
    )

    page.goto(login_url)

    page.locator(
        'input[name="username"]',
    ).fill(username)

    page.locator(
        'input[name="password"]',
    ).fill(password)

    page.get_by_role(
        "button",
        name="Sign In",
    ).click()

    page.wait_for_url(
        live_server.url + "/",
    )

    return page
