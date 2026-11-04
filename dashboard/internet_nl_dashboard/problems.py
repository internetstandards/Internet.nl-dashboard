# SPDX-License-Identifier: Apache-2.0
"""RFC 9457 errors for the dashboard API (ADR 2.2.1)."""

from enum import StrEnum
from http import HTTPStatus
from typing import Literal

from django.conf import settings
from django.http import JsonResponse
from ninja import Schema
from ninja.errors import HttpError
from pydantic import Field

# These absolute identifiers are independent of the deployment hostname. The date
# is part of the namespace, not a version; do not change it in future releases.
PROBLEM_NAMESPACE = "tag:internet.nl,2026:dashboard:"


class ProblemType(StrEnum):
    INVALID_INPUT = PROBLEM_NAMESPACE + "invalid-input"
    INVALID_CAPTCHA = PROBLEM_NAMESPACE + "invalid-captcha"
    USER_SETTINGS_NOT_FOUND = PROBLEM_NAMESPACE + "user-settings-not-found"
    UNSUPPORTED_LANGUAGE = PROBLEM_NAMESPACE + "unsupported-language"
    INVALID_EMAIL_ADDRESS = PROBLEM_NAMESPACE + "invalid-email-address"
    USERNAME_REQUIRED = PROBLEM_NAMESPACE + "username-required"
    PASSWORD_TOO_SHORT = PROBLEM_NAMESPACE + "password-too-short"
    ACCOUNT_NAME_REQUIRED = PROBLEM_NAMESPACE + "account-name-required"
    USERNAME_ALREADY_EXISTS = PROBLEM_NAMESPACE + "username-already-exists"
    ACCOUNT_NAME_ALREADY_EXISTS = PROBLEM_NAMESPACE + "account-name-already-exists"
    ACCOUNT_NOT_FOUND = PROBLEM_NAMESPACE + "account-not-found"
    LIST_NOT_FOUND = PROBLEM_NAMESPACE + "list-not-found"
    DOMAIN_LIMIT_EXCEEDED = PROBLEM_NAMESPACE + "domain-limit-exceeded"
    REPORT_SHARING_UNAVAILABLE = PROBLEM_NAMESPACE + "report-sharing-unavailable"
    DISCOVERY_NOT_STARTED = PROBLEM_NAMESPACE + "discovery-not-started"
    SCAN_ALREADY_FINISHED = PROBLEM_NAMESPACE + "scan-already-finished"
    SPREADSHEET_STORAGE_UNAVAILABLE = PROBLEM_NAMESPACE + "spreadsheet-storage-unavailable"
    SPREADSHEET_QUEUE_UNAVAILABLE = PROBLEM_NAMESPACE + "spreadsheet-queue-unavailable"
    INVALID_SPREADSHEET = PROBLEM_NAMESPACE + "invalid-spreadsheet"
    INVALID_SUGGESTION_DOMAIN = PROBLEM_NAMESPACE + "invalid-suggestion-domain"
    SUBDOMAIN_SUGGESTIONS_UNAVAILABLE = PROBLEM_NAMESPACE + "subdomain-suggestions-unavailable"
    SUBDOMAIN_SUGGESTIONS_TIMEOUT = PROBLEM_NAMESPACE + "subdomain-suggestions-timeout"
    SUBDOMAIN_SUGGESTIONS_FAILED = PROBLEM_NAMESPACE + "subdomain-suggestions-failed"
    STAFF_ACCOUNT_REQUIRED = PROBLEM_NAMESPACE + "staff-account-required"
    REPORT_ACCESS_DENIED = PROBLEM_NAMESPACE + "report-access-denied"


class FieldErrorSchema(Schema):
    loc: list[str | int] = Field(
        description="Request location (body, query or path), followed by the field or item path."
    )
    msg: str = Field(description="Human-readable validation detail; clients identify the field using loc.")


class ProblemSchema(Schema):
    type: ProblemType | Literal["about:blank"] = Field(
        default="about:blank",
        description=(
            "Stable problem type URI. Domain types are listed in ProblemType. Generic HTTP errors use about:blank. "
            "Clients must handle unrecognized types."
        ),
    )
    title: str
    status: int
    detail: str
    errors: list[FieldErrorSchema] | None = None


def problem_details(status: int, detail: str, *, problem_type: ProblemType | None = None, errors=None) -> dict:
    return ProblemSchema(
        type=str(problem_type) if problem_type else "about:blank",
        title=problem_type.name.replace("_", " ").capitalize() if problem_type else HTTPStatus(status).phrase,
        status=status,
        detail=detail,
        errors=errors,
    ).model_dump(exclude_none=True)


class ApiError(HttpError):
    """An HTTP failure with an optional domain problem type and field errors."""

    def __init__(
        self,
        status: int,
        detail: str,
        problem_type: ProblemType | None = None,
        *,
        field: str | None = None,
        errors=None,
        extensions: dict | None = None,
    ):
        super().__init__(status, detail)
        self.problem_type = problem_type
        self.errors = errors if errors is not None else ([{"loc": ["body", field], "msg": detail}] if field else None)
        self.extensions = extensions or {}


class DocumentedApiError(ApiError):
    """Define an error once for both raising it and describing it in OpenAPI."""

    status: int
    detail: str
    problem_type: ProblemType | None = None
    problem_schema: type[ProblemSchema] = ProblemSchema

    def __init__(self):
        super().__init__(self.status, self.detail, self.problem_type)

    @classmethod
    def example(cls) -> dict:
        return problem_details(cls.status, cls.detail, problem_type=cls.problem_type)


def raises(*errors: type[DocumentedApiError]):
    """Declare a function's expected API errors without wrapping its execution."""

    def decorate(operation):
        operation.api_errors = errors
        return operation

    return decorate


def problem_responses(operation, *, descriptions: dict[int, str] | None = None) -> dict:
    """Build route documentation from the errors declared by its logic function."""
    responses = {status: {"description": detail} for status, detail in (descriptions or {}).items()}
    grouped = {}
    for error in operation.api_errors:
        grouped.setdefault(error.status, []).append(error)
    for status, errors in grouped.items():
        schemas = [{"$ref": f"#/components/schemas/{error.problem_schema.__name__}"} for error in errors]
        media = {"schema": schemas[0] if all(schema == schemas[0] for schema in schemas) else {"oneOf": schemas}}
        if len(errors) == 1:
            media["example"] = errors[0].example()
        else:
            media["examples"] = {error.__name__: {"value": error.example()} for error in errors}
        responses[status] = {
            "description": " ".join(error.detail for error in errors),
            "content": {"application/problem+json": media},
        }
    return {"responses": responses}


def problem_response(
    status: int, detail: str, *, problem_type: ProblemType | None = None, errors=None, extensions=None
):
    body = problem_details(status, detail, problem_type=problem_type, errors=errors)
    if extensions:
        # RFC 9457 extensions add domain information without overriding standard members.
        body.update({name: value for name, value in extensions.items() if name not in ProblemSchema.model_fields})
    return JsonResponse(
        body,
        status=status,
        content_type="application/problem+json",
    )


class DashboardApiProblemMiddleware:
    """Cover routing, method and middleware failures outside Ninja's exception handlers."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not request.path.startswith("/api/v1/") or request.path.startswith("/api/v1/allauth/"):
            return response
        if response.status_code >= 400 and response.get("Content-Type", "").split(";")[0] != "application/problem+json":
            original = response
            response = problem_response(original.status_code, HTTPStatus(original.status_code).phrase)
            for name, value in original.headers.items():
                if name.lower() not in {"content-type", "content-length", "content-encoding"}:
                    response[name] = value
            response.cookies = original.cookies
        response["API-Version"] = settings.OPEN_API_VERSION
        return response
