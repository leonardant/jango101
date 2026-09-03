def login_not_required(view_func):
    """
    Mark a view as publicly accessible.
    """
    view_func.login_not_required = True
    return view_func