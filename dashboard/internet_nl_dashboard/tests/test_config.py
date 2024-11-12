from dashboard.internet_nl_dashboard.views.app import config_content


def test_config_content(db):
    data = config_content()

    assert data["show"]["signup_form"] is False
