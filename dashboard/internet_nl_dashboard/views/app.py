import orjson
from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from websecmap.app.constance import get_all_values

ONE_HOUR = 60 * 60


def config_content():
    configuration = get_all_values()

    return {
        "show": {
            "signup_form": configuration["SHOW_SIGNUP_FORM"],
        },
        "app": {
            "layout": configuration["SITE_LAYOUT_NAME"],
        },
    }


@cache_page(ONE_HOUR)
def config(request) -> HttpResponse:
    return HttpResponse(orjson.dumps(config_content()), content_type="application/json", status=200)
