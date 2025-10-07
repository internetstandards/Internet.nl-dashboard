from typing import Any, Dict

from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from ninja import Router, Schema
from websecmap.app.constance import get_all_values

ONE_HOUR = 60 * 60

# Ninja router for config endpoints
router = Router(tags=["config"])


class SubdomainSuggestionSchema(Schema):
    enabled: bool
    default_period: int
    default_extend_period: int


class SignupSchema(Schema):
    enabled: bool


class AppSchema(Schema):
    subdomain_suggestion: SubdomainSuggestionSchema
    signup: SignupSchema
    layout: str
    supported_languages: list[str]


class ShowSchema(Schema):
    signup_form: bool


class ConfigContentSchema(Schema):
    show: ShowSchema
    app: AppSchema
    # Include all Constance settings as a passthrough for clients that need everything
    settings: Dict[str, Any]


def config_content() -> ConfigContentSchema:
    configuration = get_all_values()

    return ConfigContentSchema(
        show=ShowSchema(
            signup_form=configuration["SHOW_SIGNUP_FORM"],
        ),
        app=AppSchema(
            subdomain_suggestion=SubdomainSuggestionSchema(
                enabled=configuration["SUBDOMAIN_SUGGESTION_ENABLED"],
                default_period=configuration["SUBDOMAIN_SUGGESTION_DEFAULT_TIME_PERIOD"],
                default_extend_period=configuration["SUBDOMAIN_SUGGESTION_DEFAULT_EXTEND_TIME_PERIOD"],
            ),
            # in the future we'll support this
            signup=SignupSchema(
                enabled=configuration["SHOW_SIGNUP_FORM"],
            ),
            layout=configuration["SITE_LAYOUT_NAME"],
            supported_languages=configuration["SUPPORTED_LANGUAGES"],
        ),
        settings=dict(configuration),
    )


@router.get("/", response={200: ConfigContentSchema})
@cache_page(ONE_HOUR)
def config_api(request) -> JsonResponse:
    return JsonResponse(config_content().dict(), status=200, safe=False)
