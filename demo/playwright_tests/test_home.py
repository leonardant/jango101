from django.urls import reverse


def test_home_page_loads_in_browser(
    page,
    live_server,
    django_user_model,
):
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

    assert page.title() != ""

    assert page.get_by_text(
        "Welcome",
        exact=True,
    ).is_visible()

    assert page.get_by_role(
        "heading",
        name="To Do Items",
    ).is_visible()
