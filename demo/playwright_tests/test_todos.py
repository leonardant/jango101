def test_todos_page_loads(
    authenticated_page,
):
    page = authenticated_page

    page.get_by_role(
        "link",
        name="To Do Items",
        exact=True,
    ).click()

    assert "/todos/" in page.url

    assert page.get_by_role(
        "heading",
        name="My To Do Items",
    ).is_visible()


def test_user_can_add_todo_item(
    authenticated_page,
):
    page = authenticated_page

    # Navigate to the To Do page.
    page.get_by_role(
        "link",
        name="To Do Items",
        exact=True,
    ).click()

    # Open the Add To Do page.
    page.get_by_role(
        "link",
        name="Add To Do Item",
        exact=True,
    ).click()

    # Confirm we are on the Add To Do page.
    assert page.get_by_role(
        "heading",
        name="Add To Do Item",
    ).is_visible()

    # Fill in the form.
    page.locator(
        'input[name="title"]',
    ).fill(
        "Buy milk",
    )

    page.locator(
        'textarea[name="description"]',
    ).fill(
        "Buy milk from the supermarket",
    )

    # Submit the form.
    page.get_by_role(
        "button",
        name="Create To Do Item",
    ).click()

    # Wait until we return to the To Do list.
    page.wait_for_url(
        "**/todos/",
    )

    # Locate the To Do table.
    todo_table = page.locator(
        "table",
    )

    # Confirm the new item appears in the table.
    assert todo_table.get_by_role(
        "cell",
        name="Buy milk",
        exact=True,
    ).is_visible()

    assert todo_table.get_by_role(
        "cell",
        name="Buy milk from the supermarket",
        exact=True,
    ).is_visible()
