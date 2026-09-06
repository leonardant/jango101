def test_user_can_toggle_todo_item(
    authenticated_page,
):
    page = authenticated_page

    # Go to the To Do page.
    page.get_by_role(
        "link",
        name="To Do Items",
        exact=True,
    ).click()

    # Create a new To Do item.
    page.get_by_role(
        "link",
        name="Add To Do Item",
        exact=True,
    ).click()

    page.locator(
        'input[name="title"]',
    ).fill(
        "Walk the dog",
    )

    page.locator(
        'textarea[name="description"]',
    ).fill(
        "Take the dog for a walk",
    )

    page.get_by_role(
        "button",
        name="Create To Do Item",
    ).click()

    page.wait_for_url(
        "**/todos/",
    )

    # Find the row containing our To Do item.
    todo_row = page.get_by_role(
        "row",
    ).filter(
        has_text="Walk the dog",
    )

    # The checkbox should initially be unchecked.
    checkbox = todo_row.get_by_role(
        "checkbox",
    )

    assert not checkbox.is_checked()

    # Toggle the item.
    checkbox.check()

    # After submission/reload, confirm it is checked.
    page.wait_for_url(
        "**/todos/",
    )

    todo_row = page.get_by_role(
        "row",
    ).filter(
        has_text="Walk the dog",
    )

    checkbox = todo_row.get_by_role(
        "checkbox",
    )

    assert checkbox.is_checked()
