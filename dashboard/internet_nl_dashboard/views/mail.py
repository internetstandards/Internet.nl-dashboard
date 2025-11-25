# SPDX-License-Identifier: Apache-2.0

from ninja import Router, Schema

from dashboard.internet_nl_dashboard.logic import OperationResponseSchema, mail
from dashboard.internet_nl_dashboard.views import json_response

router = Router(tags=["Mail"])


class UnsubscribeSchema(Schema):
    feed: str
    unsubscribe_code: str


def unsubscribe_(request, feed, unsubscribe_code):
    """
    There is no authentication required to unsubscribe. Anyone can with the right code and feed.

    :param request:
    :param feed:
    :param unsubscribe_code:
    :return:
    """
    return json_response(mail.unsubscribe(feed, unsubscribe_code))


@router.get("/unsubscribe/{feed}/{unsubscribe_code}", response={200: OperationResponseSchema})
def unsubscribe_api(request, feed: str, unsubscribe_code: str):
    # Exposed primarily to document the existing unsubscribe path in OpenAPI; the URL path remains unchanged.
    result = mail.unsubscribe(feed, unsubscribe_code)
    return OperationResponseSchema(success=not result.get("error", False), error=result.get("error", False), message=result.get("message", ""))
