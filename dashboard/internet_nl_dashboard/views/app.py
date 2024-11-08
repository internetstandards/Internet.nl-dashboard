from django.http import JsonResponse
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
            "subdomain_suggestion": {
                "enabled": configuration["SUBDOMAIN_SUGGESTION_ENABLED"],
                "default_period": configuration["SUBDOMAIN_SUGGESTION_DEFAULT_TIME_PERIOD"],
                "default_extend_period": configuration["SUBDOMAIN_SUGGESTION_DEFAULT_EXTEND_TIME_PERIOD"],
            },
            # in the future we'll support this
            "signup": {
                "enabled": configuration["SHOW_SIGNUP_FORM"],
            }
        }
    }


@cache_page(ONE_HOUR)
def config(request) -> JsonResponse:
    return JsonResponse(config_content(), status=200, safe=False)
