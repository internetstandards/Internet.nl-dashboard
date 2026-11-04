# SPDX-License-Identifier: Apache-2.0

from typing import Annotated, Literal
from urllib.parse import urlencode

from constance import config
from django.shortcuts import redirect
from django.views.decorators.http import require_safe
from ninja import Router, Schema
from pydantic import StringConstraints

from dashboard.internet_nl_dashboard.logic import mail

router = Router(tags=["Mail"])


class UnsubscribeSchema(Schema):
    feed: Literal["scan_finished"]
    unsubscribe_code: Annotated[str, StringConstraints(min_length=128, max_length=128, pattern=r"^[a-zA-Z0-9]+$")]


@require_safe
def unsubscribe_(request, feed, unsubscribe_code):
    # Existing links in sent emails open the confirmation page without changing subscriptions.
    query = urlencode({"feed": feed, "unsubscribe_code": unsubscribe_code})
    return redirect(f"{config.DASHBOARD_FRONTEND_URL.rstrip('/')}/unsubscribe?{query}")


@router.post("/unsubscriptions", response={204: None})
def unsubscribe_api(request, data: UnsubscribeSchema):
    mail.unsubscribe(data.feed, data.unsubscribe_code)
    return None
